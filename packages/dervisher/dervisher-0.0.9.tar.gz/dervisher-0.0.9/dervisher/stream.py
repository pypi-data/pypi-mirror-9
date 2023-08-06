__author__ = 'luke'

from boto.kinesis.exceptions import ResourceInUseException, ResourceNotFoundException
import time


class Stream(object):

    conn = None
    stream_name = None
    active = 'ACTIVE'
    retry_pause = 1
    timeout = -1

    def __init__(self, conn, stream_name='dervish', shard_count=1, timeout=-1, retry_pause=1):
        self.conn = conn
        self.stream_name = stream_name
        self.timeout = timeout
        self.retry_pause = retry_pause
        print "finding stream %s" % stream_name
        try:
            if self.status() == self.active:
                return
            else:
                self.wait_till_active(self.timeout, self.retry_pause)
        except ResourceInUseException, e:
            pass
        except ResourceNotFoundException, e:
            print("creating stream with %d shards" % (shard_count))
            conn.create_stream(stream_name=stream_name, shard_count=shard_count)
            self.wait_till_active(self.timeout, self.retry_pause)

    def put(self, key, data):
        if self.ready():
            start = time.time() * 1000
            self.conn.put_record(stream_name=self.stream_name, data=data, partition_key=key)
            dur = (time.time() * 1000) - start
            print("put time %d ms" % (dur))
        else:
            raise StreamNotReadyException("%s:%s" % (self.stream_name, self.status()))

    def status(self):
        r = self.conn.describe_stream(self.stream_name)
        description = r.get('StreamDescription')
        return description.get('StreamStatus')

    def wait_till_active(self, timeout=-1, retry_pause=1):
        print "waiting",
        start = time.time()
        while not self.ready():
            if timeout >= 0 and time.time() > start + timeout:
                raise StreamTimeoutException
            time.sleep(retry_pause)
            print ".",
        print "OK"
        print "stream is active"

    def ready(self):
        return self.status() == self.active


class StreamNotReadyException(Exception):
    pass


class StreamTimeoutException(Exception):
    pass
