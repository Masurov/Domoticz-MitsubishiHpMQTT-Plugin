import Domoticz
from devicemappings.devicemapping import DeviceMapping

class SetpointDeviceMapping(DeviceMapping):

    def __init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault):
        DeviceMapping.__init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
        Domoticz.Debug("DeviceMapping __init__ create : " + str(self))
        self.dzDevice = self.GetDzDevice()
        return 

    def CreateDzDevice(self, newDeviceUnit):
        dzDevice = Domoticz.Device(Name=self.deviceLabel, Unit=newDeviceUnit, Type=242, Subtype=1, DeviceID=self.GetFullDeviceId(), Used=self.usedByDefault)
        dzDevice.Create()
        return dzDevice
    
    def UpdateDz(self, intvalue):
        formatedint = "{:.2f}".format(intvalue)
        if (self.dzDevice.sValue != formatedint):
            self.dzDevice.Update(sValue = formatedint, nValue = 0)
        return

    def DzCommandToExt(self, command, level):
        return float(level)
