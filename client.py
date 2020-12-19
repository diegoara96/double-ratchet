import threading
import mqtt



def main():

    name_from = input("FROM: ")
    name_to = input("TO: ")
    client = mqtt.connect_mqtt(name_from)
    hilo1 = threading.Thread(target=mqtt.subscribe,args=(client,name_from,) )
    hilo1.start()
    while True:
        msg=input("MESSAGE: ")
        mqtt.publish(msg,name_to,client)
    


if __name__ == '__main__':
    main()