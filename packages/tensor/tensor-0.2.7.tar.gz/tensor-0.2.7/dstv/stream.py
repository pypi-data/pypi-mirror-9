import time
import json
import os

from twisted.internet import defer

from zope.interface import implements

from tensor.interfaces import ITensorSource
from tensor.objects import Source
from tensor import utils

import cv2

class DStvStream(Source):
    """
    """

    implements(ITensorSource)

    key = 'test:d48e83793c14d0f3f495f6066ba83b0031dbca69'
    url = 'http://controller.dstvmobile.com'

    def __init__(self, *a, **kw):
        Source.__init__(self, *a, **kw)
        self.channelCache = None
        self.streamCache = {}

    @defer.inlineCallbacks
    def getStream(self, id, group):

        if id in self.streamCache:
            print "Prefetched", id
            defer.returnValue(self.streamCache[id])

        data = {
            #"user_agent": "Mozilla/5.0 (Linux; U; Android 2.2; en-ca; GT-P1000M Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1", 
            "user_agent": "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7",
            "content_type": "channel", 
            "content_id": id,
            "publish_group": group 
        }

        stream = yield utils.HTTPRequest().getJson(self.url + '/api/v1/stream/', 'POST',
            headers={
                'Authorization': ['ApiKey %s' % self.key]
            },
            data=json.dumps(data)
        )

        self.streamCache[id] = stream

        defer.returnValue(stream)

    @defer.inlineCallbacks
    def get(self):

        if not self.channelCache:
            self.channelCache = yield utils.HTTPRequest().getJson(self.url + '/api/v1/channel/?limit=100',
                headers={'Authorization': ['ApiKey %s' % self.key]})

        request = self.channelCache

        channels = request['objects']
        meta = request['meta']

        for channel in channels:
            if channel['name'][:2] == 'RN':
                stream = yield self.getStream(channel['id'], 'vodacom-tanzania')

                if os.path.exists('stream.mkv'):
                    os.unlink('stream.mkv')

                try:
                    out, err, code = yield utils.fork('/usr/bin/avconv',
                        args=(
                            '-i', stream['stream_url'], 
                            '-t', '10', 
                            '-c', 'copy', 'stream.mkv'
                        ), timeout=30.0)
                except:
                    code = 1
                    err = None

                if code == 0:
                    cap = cv2.VideoCapture('stream.mkv')

                    frames = 0
                    bright = []
                    while(cap.isOpened()):
                        ret, frame = cap.read()

                        if ret:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                            r = cv2.calcHist([gray], [0], None, [256],[0,256])
                            cv2.normalize(r, r, 0, 255, cv2.NORM_MINMAX)

                            # Calculate the base intensity
                            v = sum(r)
                            ev = sum([i * (c/v) for i,c in enumerate(r)])[0]

                            frames += 1

                            bright.append(ev)
                        else:
                            break
                    cap.release()

                    if frames:
                        avsq = sum(bright)/frames
                    else:
                        avsq = 0

                    print avsq

                    defer.returnValue(
                        self.createEvent('ok', '%s SQ' % channel['name'],
                            avsq, prefix='channel.%s.sq' % channel['name'])
                    )
