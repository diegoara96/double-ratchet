from paho.mqtt import client as mqtt_client
import threading


class mqtt():
    def __init__(self,broker='52.210.173.185',port=1883,Qos=1):
        self.broker =broker
        self.port = port
        self.Qos  = Qos
        


    def subscribe(self):
        def on_connect(client, userdata, flags, rc):
            if rc != 0:
                print("Failed to connect, return code %d\n", rc)
        client = self.client
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")    
        client.subscribe(self.name_from,self.Qos)
        client.on_message = on_message
        client.loop_forever()
    

    def publish(self,msg,name_to):
        result = self.client.publish(name_to, msg,self.Qos)
        status = result[0]
        if status != 0:
            print(f"Failed to send message to {name_to} {status}")
        

    def connect_mqtt(self,name_from,username=None,password=None) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc != 0:
                print("Failed to connect, return code %d\n", rc)
            
        client = mqtt_client.Client(name_from,clean_session=False)
        if username:
            client.username_pw_set(username,password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        self.name_from = name_from
        self.client=client
        hilo1 = threading.Thread(target=self.subscribe)
        hilo1.start()