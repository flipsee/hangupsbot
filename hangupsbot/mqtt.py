from abc import ABCMeta, abstractmethod
from datetime import datetime
import paho.mqtt.client as mq
import hangupsbot

class IInput:
    __metaclass__ = ABCMeta
    
    def __init__(self, callback=None):
        self.__flagstop__ = False
        self.__callback__ = []
        if callback != None: self.__callback__.append(callback)

    def add_callback(self, callback):
        self.__callback__.append(callback)

    def cleanup(self):
        self.__flagstop__ = True

    def reply(self, msg, requestID=None):
        _result = "Reply Msg: " + str(msg)
        if requestID != None: _result = "Reply RequestID: " + str(requestID) + " Msg: " + str(msg)
        print(_result)
    
    @abstractmethod
    def run(self): raise NotImplementedError

class mqtt(IInput):
    def __init__(self, server, port, subscribe_topic, publish_topic=None, callback=None):
        super(mqtt, self).__init__(callback)
        self.last_requestID = None
        self.client = mq.Client()
        self.client.on_connect = self.__client_connect__
        self.client.on_message = self.__client_message__
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client.connect(server, int(port), 60)

    def __client_connect__(self, client, userdata, flags, rc):
        print("MQTT Subscribing to: " + str(self.subscribe_topic))
        self.client.subscribe(self.subscribe_topic)

    def __client_message__(self, client, userdata, msg):
        print("MQTT Received Topic: " + msg.topic + " Msg: " + str(msg.payload))
        _msg = msg.payload.decode(encoding="utf-8", errors="ignore")
        _topics = msg.topic.split("/")        
        requestID = _topics[-1] # last section is the msg_id
        self.last_requestID = requestID 

        #self.last_requestID = msg.topic.replace(self.subscribe_topic.replace('+','').replace('#', ''),'')
        if (self.__callback__ != None):
            for cb in self.__callback__:
                try:
                    if cb != None:
                        cb(msg=_msg, requestID=self.last_requestID)
                except Exception as ex:
                    print("MQTT Input Error: " + str(ex))

    def publish_msg(self, msg, topic=None):
        _topic = self.publish_topic
        if topic is not None: _topic = topic
        print("MQTT Publishing Message Topic: " + str(_topic) + " Msg: " + str(msg))
        self.client.publish(_topic, str(msg))

    def reply(self, requestID, msg):
        topic = str(self.publish_topic) + str(datetime.now()) + "/" + str(requestID)
        self.publish_msg(topic=topic, msg=str(msg))

    def run(self):
        print("Starting MQTT Input...")
        try:
            if self.client is not None: self.client.loop_start()
        except Exception as ex:
            print("MQTT Input Error: " + str(ex))

    def cleanup(self):
        if self.client is not None:
            self.client.loop_stop() 
            self.client.disconnect()
