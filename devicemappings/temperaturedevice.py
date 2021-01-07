import Domoticz
from devicemappings.devicemapping import DeviceMapping

class TemperatureDeviceMapping(DeviceMapping):

    def __init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault):
        DeviceMapping.__init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
        Domoticz.Debug("DeviceMapping __init__ create : " + str(self))
        self.dzDevice = self.GetDzDevice()
        return 

    def CreateDzDevice(self, newDeviceUnit):
        dzDevice = Domoticz.Device(Name=self.deviceLabel, Unit=newDeviceUnit, TypeName="Temperature", DeviceID=self.GetFullDeviceId(), Used=self.usedByDefault)
        dzDevice.Create()
        return dzDevice

    def UpdateDz(self, floatValue):
        formatedfloat = "{:.1f}".format(floatValue)
        if (self.dzDevice.sValue != formatedfloat):
            self.dzDevice.Update(sValue = formatedfloat, nValue = 0)
        return

