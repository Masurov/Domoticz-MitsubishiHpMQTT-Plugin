#           Mitsubishi Heatpump MQTT interface Plugin
#
#           Author:     Masure, 2019
#
#
#   Plugin parameter definition below will be parsed during startup and copied into Manifest.xml, this will then drive the user interface in the Hardware web page

"""
<plugin key="MitsubishiHpMqtt" name="Mitsubishi Heatpump MQTT interface Plugin" author="Masure" version="1.0" externallink="">
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Mode5" label="Heatpump MQTT topic" width="300px" required="true" default="heatpump"/>
        
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Extra verbose: (Framework logs 2+4+8+16+64 + MQTT dump)" value="Verbose+"/>
                <option label="Verbose: (Framework logs 2+4+8+16+64 + MQTT dump)" value="Verbose"/>
                <option label="Normal: (Framework logs 2+4+8)" value="Debug"/>
                <option label="None" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import time
import bijection

class MqttClient:
    Address = ""
    Port = ""
    mqttConn = None
    isConnected = False
    mqttConnectedCb = None
    mqttDisconnectedCb = None
    mqttPublishCb = None

    def __init__(self, destination, port, mqttConnectedCb, mqttDisconnectedCb, mqttPublishCb, mqttSubackCb):
        Domoticz.Debug("MqttClient::__init__")
        self.Address = destination
        self.Port = port
        self.mqttConnectedCb = mqttConnectedCb
        self.mqttDisconnectedCb = mqttDisconnectedCb
        self.mqttPublishCb = mqttPublishCb
        self.mqttSubackCb = mqttSubackCb
        self.Open()

    def __str__(self):
        Domoticz.Debug("MqttClient::__str__")
        if (self.mqttConn != None):
            return str(self.mqttConn)
        else:
            return "None"

    def Open(self):
        Domoticz.Debug("MqttClient::Open")
        if (self.mqttConn != None):
            self.Close()
        self.isConnected = False
        self.mqttConn = Domoticz.Connection(Name=self.Address, Transport="TCP/IP", Protocol="MQTT", Address=self.Address, Port=self.Port)
        self.mqttConn.Connect()

    def Connect(self):
        Domoticz.Debug("MqttClient::Connect")
        if (self.mqttConn == None):
            self.Open()
        else:
            ID = 'Domoticz_'+Parameters['Key']+'_'+str(Parameters['HardwareID'])+'_'+str(int(time.time()))
            Domoticz.Log("MQTT CONNECT ID: '" + ID + "'")
            self.mqttConn.Send({'Verb': 'CONNECT', 'ID': ID})

    def Ping(self):
        # Domoticz.Debug("MqttClient::Ping")
        if (self.mqttConn == None or not self.isConnected):
            self.Open()
        else:
            self.mqttConn.Send({'Verb': 'PING'})

    def Publish(self, topic, payload, retain = 0):
        Domoticz.Log("MqttClient::Publish " + topic + " (" + payload + ")")
        if (self.mqttConn == None or not self.isConnected):
            self.Open()
        else:
            self.mqttConn.Send({'Verb': 'PUBLISH', 'Topic': topic, 'Payload': bytearray(payload, 'utf-8'), 'Retain': retain})

    def Subscribe(self, topics):
        Domoticz.Debug("MqttClient::Subscribe")
        subscriptionlist = []
        for topic in topics:
            subscriptionlist.append({'Topic':topic, 'QoS':0})
        if (self.mqttConn == None or not self.isConnected):
            self.Open()
        else:
            self.mqttConn.Send({'Verb': 'SUBSCRIBE', 'Topics': subscriptionlist})

    def Close(self):
        Domoticz.Log("MqttClient::Close")
        #TODO: Disconnect from server
        self.mqttConn = None
        self.isConnected = False

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("MqttClient::onConnect")
        if (Status == 0):
            Domoticz.Log("Successful connect to: "+Connection.Address+":"+Connection.Port)
            self.Connect()
        else:
            Domoticz.Log("Failed to connect to: "+Connection.Address+":"+Connection.Port+", Description: "+Description)

    def onDisconnect(self, Connection):
        Domoticz.Log("MqttClient::onDisonnect Disconnected from: "+Connection.Address+":"+Connection.Port)
        self.Close()
        # TODO: Reconnect?
        if self.mqttDisconnectedCb != None:
            self.mqttDisconnectedCb()

    def onMessage(self, Connection, Data):
        topic = ''
        if 'Topic' in Data:
            topic = Data['Topic']
        payloadStr = ''
        if 'Payload' in Data:
            payloadStr = Data['Payload'].decode('utf8','replace')
            payloadStr = str(payloadStr.encode('unicode_escape'))
        #Domoticz.Debug("MqttClient::onMessage called for connection: '"+Connection.Name+"' type:'"+Data['Verb']+"' topic:'"+topic+"' payload:'" + payloadStr + "'")

        if Data['Verb'] == "CONNACK":
            self.isConnected = True
            if self.mqttConnectedCb != None:
                self.mqttConnectedCb()

        if Data['Verb'] == "SUBACK":
            if self.mqttSubackCb != None:
                self.mqttSubackCb()

        if Data['Verb'] == "PUBLISH":
            if self.mqttPublishCb != None:
                self.mqttPublishCb(topic, Data['Payload'])



class BasePlugin:
    mqttClient = None

    def __init__(self):
        self.mappedDevicesByUnit = {}
    
        self.HeatpumpTopic = None
        self.HeatpumpSetTopic = None
        self.RoomTempTopic = None
        self.HardwareID = None
        self.PluginKey = None
        return

    def onStart(self):

        try:
            Domoticz.Heartbeat(10)

            self.PluginKey = "MitsubishiHpMqtt"
            self.HardwareID = Parameters["HardwareID"]
            self.debugging = Parameters["Mode6"]
            if self.debugging == "Verbose":
                Domoticz.Debugging(2+4+8+16+64)
            if self.debugging == "Debug":
                Domoticz.Debugging(2)
            self.HeatpumpTopic = Parameters["Mode5"]
            self.HeatpumpSetTopic = self.HeatpumpTopic + "/set"
            self.RoomTempTopic = self.HeatpumpTopic + "/status"


            self.mappedDevicesByUnit = {}
            self.payloadKeyToDevice = bijection.bijection()

            Domoticz.Debug("Mapping power")
            self.powerDeviceMapping = SwitchDeviceMapping(self.PluginKey, self.HardwareID, "Power", "POW", "power", usedByDefault=True, switchType=0, dzValues = {0:"OFF", 1:"ON"})
            self.mappedDevicesByUnit[self.powerDeviceMapping.dzDevice.Unit] = self.powerDeviceMapping
            self.payloadKeyToDevice["power"] = self.powerDeviceMapping

            Domoticz.Debug("Mapping mode")
            self.modeDeviceMapping = SelectorDeviceMapping(self.PluginKey, self.HardwareID, "Mode", "MODE", "mode", usedByDefault=True, dzLevels = {'Auto':'AUTO', 'Froid':'COOL', 'Déshum.':'DRY', 'Chaud':"HEAT", 'Ventil.':'FAN'}, offHidden=True)
            self.mappedDevicesByUnit[self.modeDeviceMapping.dzDevice.Unit] = self.modeDeviceMapping
            self.payloadKeyToDevice["mode"] = self.modeDeviceMapping

            Domoticz.Debug("Mapping fan")
            self.fanDeviceMapping = SelectorDeviceMapping(self.PluginKey, self.HardwareID, "Flux", "FAN", "fan", usedByDefault=True, dzLevels = {'Auto':'AUTO', 'Silence':'QUIET', '1':'1', '2':'2', '3':'3', '4':'4'}, offHidden=True)
            self.mappedDevicesByUnit[self.fanDeviceMapping.dzDevice.Unit] = self.fanDeviceMapping
            self.payloadKeyToDevice["fan"] = self.fanDeviceMapping

            Domoticz.Debug("Mapping vane")
            self.vVaneDeviceMapping = SelectorDeviceMapping(self.PluginKey, self.HardwareID, "Inclinaison", "VVANE", "vane", usedByDefault=True, dzLevels = {'Auto':'AUTO', '1':'1', '2':'2', '3':'3', '4':'4', '5':'5', 'Oscillant':'SWING'}, offHidden=True)
            self.mappedDevicesByUnit[self.vVaneDeviceMapping.dzDevice.Unit] = self.vVaneDeviceMapping
            self.payloadKeyToDevice["vane"] = self.vVaneDeviceMapping

            Domoticz.Debug("Mapping wvane")
            self.wVaneDeviceMapping = SelectorDeviceMapping(self.PluginKey, self.HardwareID, "Direction", "WVANE", "wideVane", usedByDefault=True, dzLevels = {'<<':'<<', '<':'<', 'V':'|', '>':'>', '>>':'>>', 'Oscillant':'SWING'}, offHidden=True)
            self.mappedDevicesByUnit[self.wVaneDeviceMapping.dzDevice.Unit] = self.wVaneDeviceMapping
            self.payloadKeyToDevice["wideVane"] = self.wVaneDeviceMapping

            Domoticz.Debug("Mapping setpoint")
            self.setpointDeviceMapping = SetpointDeviceMapping(self.PluginKey, self.HardwareID, "Thermostat", "TEMPSET", "temperature", usedByDefault=True)
            self.mappedDevicesByUnit[self.setpointDeviceMapping.dzDevice.Unit] = self.setpointDeviceMapping
            self.payloadKeyToDevice["temperature"] = self.setpointDeviceMapping

            Domoticz.Debug("Mapping temperature")
            self.temperatureDevicemapping = TemperatureDeviceMapping(self.PluginKey, self.HardwareID, "T° Split", "TEMP", "roomTemperature", usedByDefault=True)
            self.mappedDevicesByUnit[self.temperatureDevicemapping.dzDevice.Unit] = self.temperatureDevicemapping


            self.mqttserveraddress = Parameters["Address"].strip()
            self.mqttserverport = Parameters["Port"].strip()
            self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, None)
        except Exception as e:
            Domoticz.Error("MQTT client start error: "+str(e))
            self.mqttClient = None
    
    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):  # react to commands arrived from Domoticz
        if self.mqttClient is None:
            return False
        Domoticz.Debug("Command: " + Command + " (" + str(Level) + ") Color:" + Color)
        try:
            Domoticz.Debug("    getting device for unit " + str(Unit))
            if (Unit in self.mappedDevicesByUnit):
                Domoticz.Debug("    found")
                Domoticz.Debug("    key : " + str(self.mappedDevicesByUnit[Unit].externalDeviceId))  
                Domoticz.Debug("    value : " + str(self.mappedDevicesByUnit[Unit].DzCommandToExt(Command, str(Level))))  
                payloaddic = { self.mappedDevicesByUnit[Unit].externalDeviceId : self.mappedDevicesByUnit[Unit].DzCommandToExt(Command, str(Level))} 
                Domoticz.Debug(str(payloaddic))

            if (not payloaddic is None):
                Domoticz.Debug("    publishing on " + self.HeatpumpSetTopic + " : " + str(json.dumps(payloaddic)))
                self.mqttClient.Publish(self.HeatpumpSetTopic, json.dumps(payloaddic))
        except Exception as e:
            Domoticz.Debug(str(e))
            return False
    
    def iif(self, boolValue, trueValue, falseValue):
        if (boolValue == True):
            return trueValue
        else:
            return falseValue
         
    def onConnect(self, Connection, Status, Description):
       if self.mqttClient is not None:
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
       if self.mqttClient is not None:
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
       if self.mqttClient is not None:
        self.mqttClient.onMessage(Connection, Data)

    def onHeartbeat(self):
        # Domoticz.Debug("Heartbeating...")
        if self.mqttClient is not None:
            try:
                # Reconnect if connection has dropped
                if (self.mqttClient.mqttConn is None) or (not self.mqttClient.isConnected):
                    Domoticz.Debug("Reconnecting")
                    self.mqttClient.Open()
                else:
                    # Domoticz.Debug("Ping...")
                    self.mqttClient.Ping()
            except Exception as e:
                Domoticz.Error(str(e))

    def onMQTTConnected(self):
        if self.mqttClient is not None:
            self.mqttClient.Subscribe([self.HeatpumpTopic, self.RoomTempTopic])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")


    def onMQTTPublish(self, topic, message): # process incoming MQTT statuses
        jsondic = json.loads(message.decode('utf8'))

        for mappedDevice in self.mappedDevicesByUnit.values():
            if (mappedDevice.externalDeviceId in jsondic):
                mappedDevice.UpdateDz(jsondic[mappedDevice.externalDeviceId])

        return 

class DeviceMapping:

    def GetNextDeviceId(self):
        nextDeviceId = 1

        while True:
            exists = False
            for device in Devices:
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
        for device in Devices:
            if (Devices[device].DeviceID == self.GetFullDeviceId()) :
                return Devices[device]
        return None

    def GetDzDevice(self):
        dzDevice = self.GetDeviceByDeviceId()
        if (dzDevice is None):
            dzDevice = self.CreateDzDevice(self.GetNextDeviceId())
        else:
            Domoticz.Log("Power device already exists")
        return dzDevice
        
    def UpdateDz(self, value):
        # implement in derived classes
        return

    def DzCommandToExt(self, command, level):
        # implement in derived classes
        return

    def ImageFileName(self, imageKey):
        return imageKey + '.zip'

    def __init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault):
        self.pluginKey = pluginKey
        self.deviceLabel = deviceLabel
        self.deviceKeyname = deviceKeyname
        self.usedByDefault = usedByDefault
        self.hardwareId = hardwareId
        self.externalDeviceId = externalDeviceId
        return 
    
class SwitchDeviceMapping(DeviceMapping):   
    
    def ImageKey(self):
        return self.pluginKey + self.deviceKeyname

    def __init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault, switchType, dzValues):
        DeviceMapping.__init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
        self.switchType = switchType
        self.dzLevelValueToExt = bijection.bijection(dzValues)

        if(self.ImageKey() not in Images):
           Domoticz.Image(Filename=self.ImageFileName(self.ImageKey())).Create() 

        if (self.ImageKey() in Images):
            self.switchImage = Images[self.ImageKey()].ID
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


class SelectorDeviceMapping(DeviceMapping):
    
    def __init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault, dzLevels, offHidden, dropdownStyle=False):
        DeviceMapping.__init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
        self.offHidden = offHidden

        if (dropdownStyle):
            self.selectorStyle = "1"
        else:
            self.selectorStyle = "0"
        
        Domoticz.Debug("SelectorDeviceMapping init : dzLevels dic init")
        
        #adds a dummy items at the beginning of supplied dic
        if (offHidden):
            dzLevels = {"": "", **dzLevels}

        #build selector level value <=> external value dic
        self.dzLevelValueToExt = bijection.bijection()
        self.dzLevelValueToLabel = bijection.bijection()
        

        Domoticz.Debug("SelectorDeviceMapping init : dzLevelValueToExt, dzLevelValueToLabel  init")

        levelvalue = 0
        for (levelname, extlevel) in dzLevels.items():
            self.dzLevelValueToExt[str(levelvalue)] = extlevel
            self.dzLevelValueToLabel[str(levelvalue)] = levelname
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

            if(levelImageKey not in Images):
                Domoticz.Image(self.ImageFileName(levelImageKey)).Create() 

            if(levelImageKey in Images):
                self.imageIdByValue[levelValue] = Images[levelImageKey].ID
            else:
                self.imageIdByValue[levelValue] = None

    def CreateDzDevice(self, newDeviceUnit):
        levelsActions = "|".join(["" for k in self.dzLevelValueToLabel.keys()])
        levelNames = "|".join(self.dzLevelValueToLabel.values())
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

class SetpointDeviceMapping(DeviceMapping):

    def __init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault):
        DeviceMapping.__init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
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
        return int(float(level))

class TemperatureDeviceMapping(DeviceMapping):

    def __init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault):
        DeviceMapping.__init__(self, pluginKey, hardwareId, deviceLabel, deviceKeyname, externalDeviceId, usedByDefault)
        
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

global _plugin

_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()