__author__ = 'lsamaha'

from shard import Shard


class Post(object):

    stream = None
    shard = None

    def __init__(self, stream, shard=Shard()):
        self.stream = stream
        self.shard = shard

    def event(self, event):
        print("posting %s" % (event.tojson()))
        self.stream.put(self.shard.get(event), event.tojson())




