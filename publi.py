# python 3.6
import random
import time
from paho.mqtt import client as mqtt_client
broker = '52.210.173.185'
port =    1883
topic = "/python/mqtt"
# generate client ID with pub prefix randomly
client_id = "publi"
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id,clean_session=False)
    client.username_pw_set(username="sinf",password="snif20")
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg,1)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic} {status}")
        msg_count += 1
def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
if __name__ == '__main__':
    run()