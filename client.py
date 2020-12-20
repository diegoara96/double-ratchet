from paho.mqtt import client as mqtt_client
import threading
from doublerachet import Rachet
import doublerachet
import json


broker='52.210.173.185'
port=1883
Qos=0
result_available = threading.Event()


def main():
    name_from = input("FROM: ")
    name_to = input("TO: ")
    rachet=Rachet()
    server=connect_mqtt(name_from,"sinf","snif20")
    hilo1 = threading.Thread(target=subscribe,args=(server,name_from,rachet,name_to))
    hilo1.start()


    while True:
        message=input("MESSAGE: ")
        if(doublerachet.getPublicDHr(rachet)==doublerachet.getPublicDH(rachet)):
            msg=json.dumps({"DH":None,"C":None})
            publish(server,msg,name_to)
            result_available.wait()
            print("clave publica")
        message=doublerachet.RatchetEncrypt(rachet,message)
        publish(server,message,name_to)
    


def subscribe(client,name_from,rachet:Rachet,name_to):
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)
    client.on_connect = on_connect
    client.connect(broker, port)
    def on_message(client, userdata, msg):
        response=json.loads(msg.payload.decode())
        if response["C"]==None:
            if response["DH"]!=None:
                doublerachet.setDHr(rachet,response)  
                result_available.set()
            else:
                public = doublerachet.getPublicDH(rachet=rachet)
                param = doublerachet.getParametersDH(rachet=rachet)
                message=json.dumps({"DH":public,"PN":rachet.PN, "N":rachet.Ns,"C":None,"PAM":param})
                publish(client,message,name_to)
                print("enviando parametros")
        else:            
            messaege=doublerachet.RatchetDecrypt(rachet,response)
            print(messaege)
       
    client.subscribe(name_from,Qos)
    client.on_message = on_message
    client.loop_forever()


def publish(client,msg,name_to):
    result = client.publish(name_to, msg,Qos)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to {name_to} {status}")
    

def connect_mqtt(name_from,username=None,password=None) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)
        
    client = mqtt_client.Client(name_from,clean_session=True)
    if username:
        client.username_pw_set(username,password)
    client.on_connect = on_connect
    client.connect(broker,port)
    return client



if __name__ == '__main__':
    main()
    