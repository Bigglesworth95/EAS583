import hashlib
import os

def myhash(m):
    #Generate random nonce
    nonce = os.urandom(64)
    #Generate hex digest
    h_hex = hashlib.sha256(m)
    return nonce, h_hex
