#!/bin/bash
__author__ = 'lsamaha'

import sys, signal, time
import threading
from dervisher import Dervisher
from event import Event
from post import Post
from stream import Stream
from boto.kinesis.layer1 import KinesisConnection

class Whirling(Dervisher):

    whirling = False
    mimi = None
    timer = None
    dance = ['back','forth']
    count = 0

    def start(self, rpm):
        Dervisher.start(self)
        self.timer = WhirlTimer(rpm, self.whirl)
        self.timer.start()
        self.whirling = True

    def stop(self):
        self.timer.stop()
        Dervisher.stop(self)

    def whirl(self):
        step = self.dance[self.count % len(self.dance)]
        self.post.event(Event(event_class='start', event_type='whirl', subtype=step, env='dev', product=self.product))
        self.post.event(Event(event_class='complete', event_type='whirl', subtype=step, env='dev', product=self.product))
        self.count += 1

    def sig(self, signal, frame):
        print "received signal %s" % signal
        self.stop()

class WhirlTimer(threading.Thread):

    stopped = False

    def __init__(self, rpm, callback):
        threading.Thread.__init__(self)
        self.wait_time = rpm / 60
        self.callback = callback
        self.daemon = True
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(self.wait_time):
            self.callback()

    def stop(self):
        self.stopped = True

def main():
    if len(sys.argv) < 2:
        print "usage: whirl rpm"
    else:
        rpm = int(sys.argv[1])
        print "a dervisher starts whirling at %d rpm" % rpm
        dervisher = Whirling(product = 'mimi', post=Post(stream=Stream(KinesisConnection())))
        dervisher.start(rpm)
        signal.signal(signal.SIGINT, dervisher.sig)
        while(dervisher.whirling):
            time.sleep(1)

if __name__ == "__main__":
    main()




