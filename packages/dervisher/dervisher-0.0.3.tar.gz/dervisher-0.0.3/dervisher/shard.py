__author__ = 'luke'

import uuid


class Shard(object):

    def get(self, event):
        return str(uuid.uuid4())
