import threading
from paho.mqtt import client as mqtt_client

broker = '52.210.173.185'
port =  1883
Qos = 1

def subscribe(client,name_from):
    print(name_from)
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
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
        if status == 0:
            print(f"Send `{msg}` to `{name_to}`")
        else:
            print(f"Failed to send message to {name_to} {status}")
    
    


def connect_mqtt(name_from) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)    
    client = mqtt_client.Client(name_from,clean_session=False)
    client.username_pw_set(username="sinf",password="snif20")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def main():

    name_from = input("FROM: ")
    name_to = input("TO: ")
    client = connect_mqtt(name_from)
    hilo1 = threading.Thread(target=subscribe,args=(client,name_from,) )
    hilo1.start()
    while True:
        msg=input("MESSAGE: ")
        publish(msg,name_to,client)
    
























if __name__ == '__main__':
    main()