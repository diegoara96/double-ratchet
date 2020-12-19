from paho.mqtt import client as mqtt_client

broker = '52.210.173.185'
port =  1883
Qos = 1

def subscribe(client,name_from):
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)

    client.on_connect = on_connect
    client.connect(broker, port)
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")    
    client.subscribe(name_from,Qos)
    client.on_message = on_message
    client.loop_forever()


def publish(msg,name_to,client):
    result = client.publish(name_to, msg,Qos)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to {name_to} {status}")
    
    


def connect_mqtt(name_from) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)
        
    client = mqtt_client.Client(name_from,clean_session=False)
    client.username_pw_set(username="sinf",password="snif20")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


