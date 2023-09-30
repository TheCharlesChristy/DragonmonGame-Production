from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from datetime import datetime
def loadkeys():
    privatekey = open("server-private-key.pem", "rb")
    privatekey = serialization.load_pem_private_key(
        privatekey.read(),
        password=bytes(str(input("Password")), "utf-8"),
        backend=default_backend()
    )
    publickeycertfile = open("server-public-key.pem", "r")
    publickeycertfiledata = bytes(publickeycertfile.read(), "utf-8")
    publickeycert = x509.load_pem_x509_certificate(
        publickeycertfiledata,
        backend=default_backend())
    publickey = publickeycert.public_key()
    return privatekey, publickey

def loadshortkeys(password):
    shortprivatekey = open("short-private-key.pem", "rb")
    shortprivatekey = serialization.load_pem_private_key(
        shortprivatekey.read(),
        password=bytes(password, "utf-8"),
        backend=default_backend()
    )
    shortpublickeyfile = open("short-public-key.pem", "r")
    shortpublickeyfiledata = bytes(shortpublickeyfile.read(), "utf-8")
    shortcert = x509.load_pem_x509_certificate(
        shortpublickeyfiledata,
        backend=default_backend())
    shortpublickey = shortcert.public_key()
    return shortprivatekey, shortpublickey, shortcert


def encryptdata(data, publickey):
    encrypted = publickey.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

def decryptdata(data, privatekey):
    decrypted = privatekey.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted

def checkshortkeys(cert):
    certexpiredate = cert.not_valid_after
    currentdate = datetime.now()
    if currentdate > certexpiredate:
        return False
    else:
        return True



    