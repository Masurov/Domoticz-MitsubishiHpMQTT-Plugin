import Domoticz
from devicemappings.devicemapping import DeviceMapping
import bijection

class SelectorDeviceMapping(DeviceMapping):
    
    def __init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault, dzLevelsCodes, offHidden, dropdownStyle=False):
        DeviceMapping.__init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
        self.offHidden = offHidden

        if (dropdownStyle):
            self.selectorStyle = "1"
        else:
            self.selectorStyle = "0"
        
        Domoticz.Debug("SelectorDeviceMapping init : dzLevels dic init")
        
        #adds a dummy items at the beginning of supplied list
        if (offHidden):
            dzLevelsCodes.insert(0, ("",""))

        #build selector level value <=> external value dic
        self.dzLevels = []
        self.dzLevelValueToLabel = bijection.Bijection()
        self.dzLevelValueToExt = bijection.Bijection()
        
        levelvalue = 0
        for labelCodeTuple in dzLevelsCodes:
            self.dzLevels.append(labelCodeTuple[0])
            self.dzLevelValueToLabel[str(levelvalue)] = labelCodeTuple[0]
            self.dzLevelValueToExt[str(levelvalue)] = labelCodeTuple[1]
            levelvalue += 10
        
        self.InitLevelImages()

        Domoticz.Debug("DeviceMapping __init__ create : " + str(self))
        self.dzDevice = self.GetDzDevice()
        return 

    def ImageKey(self, levelValue):
        return self.pluginKey + self.deviceKeyname + levelValue

    def InitLevelImages(self):
        self.imageIdByValue = {}
        for levelValue in self.dzLevelValueToExt.keys():
            
            if (levelValue == '0' and self.offHidden):
                continue

            levelImageKey = self.ImageKey(levelValue)

            if(levelImageKey not in self.pluginImages):
                Domoticz.Image(self.ImageFileName(levelImageKey)).Create() 

            if(levelImageKey in self.pluginImages):
                self.imageIdByValue[levelValue] = self.pluginImages[levelImageKey].ID
            else:
                self.imageIdByValue[levelValue] = None

    def CreateDzDevice(self, newDeviceUnit):
        levelsActions = "|".join(["" for k in self.dzLevels])
        levelNames = "|".join(self.dzLevels)
        levelOffHidden = "false"
        if (self.offHidden):
            levelOffHidden = "true"

        options = {"LevelActions": levelsActions, "LevelNames": levelNames, "LevelOffHidden": levelOffHidden, "SelectorStyle": self.selectorStyle}
        dzDevice = Domoticz.Device(Name=self.deviceLabel, Unit=newDeviceUnit, TypeName="Selector Switch", Switchtype=18, DeviceID=self.GetFullDeviceId(), Options=options, Used=self.usedByDefault)
        dzDevice.Create()
        return dzDevice

    def UpdateDz(self, value):
        if (value in self.dzLevelValueToExt.inverse):
            sValue =self.dzLevelValueToExt.inverse[value]
            if (self.dzDevice.sValue != sValue):
                if (not self.imageIdByValue[sValue] is None):
                    self.dzDevice.Update(nValue = 0, sValue = sValue, Image = self.imageIdByValue[sValue])
                else:
                    self.dzDevice.Update(nValue = 0, sValue = sValue)
        return

    def DzCommandToExt(self, command, level):
        if (level in self.dzLevelValueToExt):
            return self.dzLevelValueToExt[level]
        else:
            return None

