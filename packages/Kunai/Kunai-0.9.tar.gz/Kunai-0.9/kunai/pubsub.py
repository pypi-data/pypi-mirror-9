from kunai.log import logger


# Starting a pub-sub system for global set
class PubSub(object):
    def __init__(self):
        self.registered = {}


    # Subscribe to a thread
    def sub(self, k, f):
        if not k in self.registered:
            self.registered[k] = []
        self.registered[k].append(f)

    
    # Call all subscribed function of a thread, and accept args if need
    def pub(self, k, **args):
        if not k in self.registered:
            logger.warning('Call on a pub on a unregistered key %s' % k)
            return
        l = self.registered[k]
        for f in l:
            f(**args)
        

pubsub = PubSub()
