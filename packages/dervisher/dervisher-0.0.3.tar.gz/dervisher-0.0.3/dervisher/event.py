__author__ = 'lsamaha'

import json


class Event(object):

    event_class = None
    event_type = None
    subtype = None
    product = None
    env = None
    pretty = None

    def __init__(self, event_class, event_type, subtype, product, env, pretty=False):
        self.event_class = event_class
        self.event_type = event_type
        self.subtype = subtype
        self.product = product
        self.env = env
        self.pretty = pretty

    def tojson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4 if self.pretty else None)








