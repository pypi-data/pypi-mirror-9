__author__ = 'lsamaha'

from stream import Stream
from shard import Shard
from boto.kinesis.layer1 import KinesisConnection


class Post(object):

    stream = None
    shard = None

    def __init__(self, stream=Stream(conn=KinesisConnection()), shard=Shard()):
        self.stream = stream
        self.shard = shard

    def event(self, event):
        print("posting %s" % (event.tojson()))
        self.stream.put(self.shard.get(event), event.tojson())




