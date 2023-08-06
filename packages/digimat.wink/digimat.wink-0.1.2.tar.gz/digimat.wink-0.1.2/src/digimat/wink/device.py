import time
from pprint import pprint

from wink import Wink

class WinkDevice(object):
    def __init__(self, wink, dtype, did, config={}):
        self._wink=wink
        self._dtype=dtype
        self._did=did
        if not config:
            config={}
        self._config=config
        self._stampConfig=0

    @property
    def wink(self):
        return self._wink

    def _combineDicts(self, dictionary1, dictionary2):
        output = {}
        for item, value in dictionary1.iteritems():
            if dictionary2.has_key(item):
                if isinstance(dictionary2[item], dict):
                    output[item] = self._combineDicts(value, dictionary2.pop(item))
            else:
                output[item] = value
        for item, value in dictionary2.iteritems():
             output[item] = value
        return output

    def mergeConfig(self, config):
        if config:
            self._config=self._combineDicts(self._config, config)
        return self._config

    def readConfig(self):
        config=self.wink.requestGET('/%s/%s' % (self._dtype, self._did))
        if config:
            self._stampConfig=time.time()
            return self.mergeConfig(config)

    def writeConfig(self, data=None):
        if not data:
            data=self._config
        if data:
            config=self.wink.requestPUT('/%s/%s' % (self._dtype, self._did), data)
            if config:
                self._stampConfig=time.time()
                self.mergeConfig(config)
        return self._config

    def updateConfig(self, data):
        return self.mergeConfig(data)

    def flush(self):
        self.writeConfig()

    def dump(self):
        pprint(self._config)




if __name__ == "__main__":
    pass
