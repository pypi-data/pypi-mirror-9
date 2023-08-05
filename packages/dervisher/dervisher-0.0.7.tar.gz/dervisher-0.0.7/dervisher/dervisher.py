__author__ = 'lsamaha'

from event import Event


class Dervisher(object):

    product = None
    post = None

    def __init__(self, product, post):
        self.product = product
        self.post = post

    def start(self, rpm):
        self.post.event(
            Event(event_class='start', event_type='service', subtype='whirl', env='dev', product=self.product))

    def stop(self):
        self.post.event(
            Event(event_class='stop', event_type='service', subtype='whirl', env='dev', product=self.product))

