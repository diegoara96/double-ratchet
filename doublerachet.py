from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

class Rachet():
    def __init__(self):
        self.parameters = dh.generate_parameters(generator=2, key_size=2048,backend=default_backend())
        self.private_key = self.parameters.generate_private_key()
        self.public_key = self.private_key.public_key()
        self.rk = b'V\xb6\xb1\x92&!Q~\xcd\x7f\xb1\xf5\xee\xefJ\xeb'

    def dhstep(self,peer_public_key):
        shared_key = self.private_key.exchange(peer_public_key)
        return shared_key

def kdf_rk(rk,dh_out):
    derived_key = HKDF(algorithm=hashes.SHA256(),length=64,salt=rk,info=b'kdf_rk',backend=default_backend()).derive(dh_out)
    return (derived_key[0:32],derived_key[32:64]) #(32-byte root key, 32-byte chain key)


def kdf_ck(ck):
    h = hmac.HMAC(ck, hashes.SHA256(),backend=default_backend())
    h.update(b"0x01")
    d=h.copy()
    d.update(b'0x02')
    mk=d.finalize()
    ck=h.finalize()
    return (mk,ck)
    

def encrypt(msg:str,key):
    aesgcm = AESGCM(key)
    nonce=b'12345'
    ct = aesgcm.encrypt(nonce, msg.encode(),associated_data=None)
    return ct


def decrypt(ct,key):
    aesgcm = AESGCM(key)
    nonce=b'12345'
    msg=aesgcm.decrypt(nonce, ct,associated_data=None)
    return msg.decode()