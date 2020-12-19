import mqtt
from doublerachet import Rachet
import doublerachet

def main():

    name_from = input("FROM: ")
    name_to = input("TO: ")
    server=  mqtt.mqtt()
    server.connect_mqtt(name_from,"sinf","snif20")

  


    while True:
        msg=input("MESSAGE: ")
        server.publish(msg,name_to)
    



def rachet():
    alice = Rachet()
    pk_a = alice.public_key
    bob = Rachet()
    pk_b=bob.public_key
    dh_out=alice.dhstep(pk_b)
    rk,ck=doublerachet.kdf_rk(alice.rk,dh_out)
    mk,ck=doublerachet.kdf_ck(ck)
    ct=doublerachet.encrypt("test",mk)
    print(ct)
    msg=doublerachet.decrypt(ct,mk)
    print(msg)

    


if __name__ == '__main__':
    #main()
    rachet()