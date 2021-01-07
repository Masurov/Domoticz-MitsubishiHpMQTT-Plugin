import Domoticz
from devicemappings.devicemapping import DeviceMapping
import bijection

class SwitchDeviceMapping(DeviceMapping):   
    
    def ImageKey(self):
        return self.pluginKey + self.deviceKeyname

    def __init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault, switchType, dzValues):
        DeviceMapping.__init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
        self.switchType = switchType
        self.dzLevelValueToExt = bijection.Bijection(dzValues)

        if(self.ImageKey() not in self.pluginImages):
           Domoticz.Image(Filename=self.ImageFileName(self.ImageKey())).Create() 

        if (self.ImageKey() in self.pluginImages):
            self.switchImage = self.pluginImages[self.ImageKey()].ID
        else:
            self.switchImage = None

        
        Domoticz.Debug("DeviceMapping __init__ create : " + str(self))
        self.dzDevice = self.GetDzDevice()
        return 

    def CreateDzDevice(self, newDeviceUnit):
        if (not self.switchImage is None):
            dzDevice = Domoticz.Device(Name=self.deviceLabel, Unit=newDeviceUnit, TypeName="Switch", Switchtype=self.switchType, DeviceID=self.GetFullDeviceId(), Used=self.usedByDefault, Image=self.switchImage)
        else:
            dzDevice = Domoticz.Device(Name=self.deviceLabel, Unit=newDeviceUnit, TypeName="Switch", Switchtype=self.switchType, DeviceID=self.GetFullDeviceId(), Used=self.usedByDefault)
        dzDevice.Create()
        return dzDevice

    def UpdateDz(self, value):
        if (value in self.dzLevelValueToExt.inverse):
            nvalue = self.dzLevelValueToExt.inverse[value]
            if (self.dzDevice.nValue != nvalue):
                if (not self.switchImage is None):
                    Domoticz.Debug("switchImage : " + str(self.switchImage))
                    self.dzDevice.Update(nValue = nvalue, sValue = '', Image=self.switchImage)
                else:
                    self.dzDevice.Update(nValue = nvalue, sValue = '')
        return

    def DzCommandToExt(self, command, level):
        #transform command string to nvalue
        nvalue = 0
        if (command == 'On'):
            nvalue = 1

        #because mapping dic is buit on nvalues
        if (nvalue in self.dzLevelValueToExt):
            return self.dzLevelValueToExt[nvalue]
        else:
            return None


