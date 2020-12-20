from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_parameters
import json
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, ParameterFormat
import base64

MAX_SKIP =10

class Rachet():
    def __init__(self):
        self.parameters = dh.generate_parameters(generator=2, key_size=512,backend=default_backend())
        self.DHs = self.parameters.generate_private_key()
        self.DHr =self.DHs.public_key()
        self.PN=0
        self.Ns=0
        self.Nr=0
        self.CKr=0
        self.CKs=0
        self.RK = b'V\xb6\xb1\x92&!Q~\xcd\x7f\xb1\xf5\xee\xefJ\xeb'
        self.MKSKIPPED={}


def dhstep(private_key,peer_public_key):
    shared_key = private_key.exchange(peer_public_key)
    return shared_key

def kdf_rk(rk,dh_out):
    derived_key = HKDF(algorithm=hashes.SHA256(),length=64,salt=rk,info=b'kdf_rk',backend=default_backend()).derive(dh_out)
    return (derived_key[0:32],derived_key[32:64]) #(32-byte root key, 32-byte chain key)


def kdf_ck(ck):
    h = hmac.HMAC(ck, hashes.SHA256(),backend=default_backend())
    h.update(b"0x01")
    d=h.copy()
    d.update(b'0x02')
    mk=h.finalize()
    ck=d.finalize()
    return (ck,mk)
    

def DHRatchet(state:Rachet, DHr:dh.DHPublicKey):
    state.PN = state.Ns                          
    state.Ns = 0
    state.Nr = 0
    state.DHr = DHr
    state.RK, state.CKr = kdf_rk(state.RK, dhstep(state.DHs, state.DHr))
    state.DHs = state.parameters.generate_private_key()
    state.RK, state.CKs = kdf_rk(state.RK, dhstep(state.DHs, state.DHr))


def RatchetEncrypt(rachet, plaintext):
    rachet.CKs, mk = kdf_ck(rachet.CKs)
    response =  json.dumps({"DH":getPublicDH(rachet), "PN":rachet.PN, "N":rachet.Ns,"C":encrypt(plaintext,mk)})
    rachet.Ns += 1
    print(mk)
    return response

def RatchetDecrypt(rachet, response):
    plaintext = TrySkippedMessageKeys(rachet, response)
    if plaintext != None:
        return plaintext
    DHr=load_pem_public_key(bytes(response["DH"],encoding='utf-8'), backend=default_backend())
    if response["DH"] != getPublicDHr(rachet): 
        print("clave publica diferente")
        SkipMessageKeys(rachet, response["PN"])          
        DHRatchet(rachet, DHr)
    SkipMessageKeys(rachet, response["PN"])           
    rachet.CKr, mk = kdf_ck(rachet.CKr)
    print(mk)
    rachet.Nr += 1
    return decrypt(response["C"],mk)

def TrySkippedMessageKeys(state:Rachet, response):
    if (response["DH"], response["N"]) in state.MKSKIPPED:
        mk = state.MKSKIPPED[response["DH"], response["N"]]
        del state.MKSKIPPED[response["DH"], response["N"]]
        return decrypt(response["C"],mk )
    else:
        return None

def SkipMessageKeys(state, until):
    if state.Nr + MAX_SKIP < until:
        raise Exception()
    if state.CKr != None:
        while state.Nr < until:
            state.CKr, mk = kdf_ck(state.CKr)
            state.MKSKIPPED[state.DHr, state.Nr] = mk
            state.Nr += 1

def encrypt(msg:str,key):
    aesgcm = AESGCM(key)
    nonce=b'12345'
    ct = aesgcm.encrypt(nonce, msg.encode(),associated_data=None)
    return str(base64.urlsafe_b64encode(ct),encoding='utf-8')


def decrypt(ct,key):
    
    aesgcm = AESGCM(key)
    nonce=b'12345'
    msg=aesgcm.decrypt(nonce, base64.urlsafe_b64decode(bytes(ct,encoding='utf-8')),associated_data=None)
    return msg.decode()

def setDHr(rachet:Rachet,response):
    rachet.DHr=load_pem_public_key(bytes(response["DH"],encoding='utf-8'), backend=default_backend())
    setParameterDH(rachet,response)
    rachet.DHs=rachet.parameters.generate_private_key()
    rachet.RK,rachet.CKs= kdf_rk(rachet.RK,dhstep(rachet.DHs,rachet.DHr))

def getPublicDH(rachet:Rachet):
   return str(rachet.DHs.public_key().public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo),encoding='utf-8')

def getPublicDHr(rachet:Rachet):
    return str(rachet.DHr.public_bytes(Encoding.PEM,PublicFormat.SubjectPublicKeyInfo),encoding='utf-8')

def getParametersDH(rachet:Rachet):
    return str(rachet.parameters.parameter_bytes(Encoding.PEM,ParameterFormat.PKCS3),encoding='utf-8')

def setParameterDH(rachet:Rachet,response):
    rachet.parameters=load_pem_parameters(bytes(response["PAM"],encoding='utf-8'), backend=default_backend())
