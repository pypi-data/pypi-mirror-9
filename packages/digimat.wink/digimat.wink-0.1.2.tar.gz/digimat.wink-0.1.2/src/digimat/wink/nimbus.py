from pprint import pprint

from device import WinkDevice

class WinkNimbus(WinkDevice):
    def __init__(self, wink, did):
        super(WinkNimbus, self).__init__(wink, 'cloud_clocks', did)
        self._dials=[None, None, None, None]

    def dial(self, index):
        try:
            dial=self._dials[index]
            if not dial:
                try:
                    config=self._config['dials']
                except:
                    config=self.readConfig()['dials']
                for dconfig in config:
                    if dconfig['dial_index']==index:
                        did=dconfig['dial_id']
                        self._dials[index]=WinkNimbusDial(self.wink, did, dconfig)
                        break
            return self._dials[index]
        except:
            pass


class WinkNimbusDial(WinkDevice):
    def __init__(self, wink, did, config):
        super(WinkNimbusDial, self).__init__(wink, 'dials', did, config)

    def setManual(self):
        # this is how to define a manual dial, only really interresting running mode ;)
        data={u'channel_configuration': {'channel_id': 10}}
        self.updateConfig(data)

    def setMinimum(self, value, position=135):
        data={'dial_configuration': {'min_position': int(position), 'min_value':float(value)}}
        self.updateConfig(data)

    def setMaximum(self, value, position=-135):
        data={'dial_configuration': {'max_position': int(position), 'max_value':float(value)}}
        self.updateConfig(data)

    def setTicks(self, ticks):
        data={'dial_configuration': {'num_ticks': int(ticks)}}
        self.updateConfig(data)

    def setLinear(self):
        data={'dial_configuration': {'scale_type': 'linear'}}
        self.updateConfig(data)

    def setForwardRotation(self):
        data={'dial_configuration': {'rotation': 'cw'}}
        self.updateConfig(data)

    def setReverseRotation(self):
        data={'dial_configuration': {'rotation': 'ccw'}}
        self.updateConfig(data)

    def setLabel(self, labelPrimary, labelSecondary=None):
        labels=[labelPrimary]
        if labelSecondary:
            labels.append(labelSecondary)
        data={'label':labelPrimary, 'labels':labels}
        self.updateConfig(data)

    def setValue(self, value):
        cvalue=self.value
        if cvalue is not None:
            if value<cvalue:
                self.setReverseRotation()
            else:
                self.setForwardRotation()
        data={'value':float(value)}
        self.updateConfig(data)

    def setBrightness(self, level):
        data={'brightness':int(level)}
        self.updateConfig(data)

    def updateValue(self, value=None, label=None, brightness=None):
        if value is not None:
            self.setValue(value)
        if label is not None:
            self.setLabel(label)
        if brightness is not None:
            self.setBrightness(brightness)
        self.flush()

    def setupGauge(self, vmin=0, vmax=100):
        self.setManual()
        self.setLinear()
        self.setMinimum(vmin, -135)
        self.setMaximum(vmax, 135)
        self.setTicks(270)

    @property
    def value(self):
        try:
            return float(self._config['value'])
        except:
            return None
        


if __name__ == "__main__":
    pass
