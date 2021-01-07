import Domoticz

class DeviceMapping:

    def GetNextDeviceId(self):
        nextDeviceId = 1

        while True:
            exists = False
            for device in self.allDevices:
                if (device == nextDeviceId) :
                    exists = True
                    break
            if (not exists):
                break
            nextDeviceId = nextDeviceId + 1

        return nextDeviceId
    
    def GetFullDeviceId(self):
        return str(self.hardwareId) + "_" + self.deviceKeyname

    def CreateDzDevice(self, newDeviceUnit):
        # implement in derived classes
        return

    def GetDeviceByDeviceId(self):
        for device in self.allDevices:
            if (self.allDevices[device].DeviceID == self.GetFullDeviceId()) :
                return self.allDevices[device]
        return None

    def GetDzDevice(self):
        dzDevice = self.GetDeviceByDeviceId()
        if (dzDevice is None):
            dzDevice = self.CreateDzDevice(self.GetNextDeviceId())
        else:
            Domoticz.Log("Device named \"{}\" (key : {}) already exists".format(self.deviceLabel, self.deviceKeyname))
        return dzDevice
        
    def UpdateDz(self, value):
        # implement in derived classes
        return

    def DzCommandToExt(self, command, level):
        # implement in derived classes
        return

    def ImageFileName(self, imageKey):
        return imageKey + '.zip'

    def __init__(self, allDevices, pluginImages, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault):
        self.pluginKey = pluginKey
        self.deviceLabel = deviceLabel
        self.deviceKeyname = deviceKeyname
        self.usedByDefault = usedByDefault
        self.hardwareId = hardwareId
        self.externalDeviceId = externalDeviceId
        self.allDevices = allDevices
        self.pluginImages = pluginImages
        return 
    
