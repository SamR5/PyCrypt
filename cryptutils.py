#!/usr/bin/python3
# -*- coding: utf-8 -*-


import time
import hashlib
import os
import pickle as pk
    

def path_size(path):
    """Return the size path in octets (either file or folder)"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    s = 0
    for root, folds, files in os.walk(path):
        for f in files:
            try:
                if not os.path.islink(f):
                    s += os.path.getsize(os.path.join(root, f))
            except: # bug with hidden files on windows
                pass
    return s

def test_encryption_speed(size):
    """Return the encryption/decryption time for <size> octets"""
    name = "speed_test.temp"
    with open(name, 'wb') as test:
        test.truncate(size)
    # time the encryption
    t0 = time.time()
    data = {}
    with open(name, 'rb') as fileToEncrypt:
        data["file"] = encrypt_bytes(fileToEncrypt.read(), 'azAZ09')
    hashedKey = hash_key('azAZ09')
    data["key"] = hashedKey[:64]
    with open(name+'.crypted', 'wb') as cryptedFile:
        pk.dump(data, cryptedFile)
    t1 = time.time()
    # time the decryption
    hash_key('azAZ09') == data["key"]
    with open(name, 'wb') as decryFile:
        decryFile.write(decrypt_bytes(data["file"], 'azAZ09'))
    t2 = time.time()
    os.remove(name)
    os.remove(name+".crypted")
    return (t1 - t0), (t2 - t1)

def encrypt_bytes(plaintext, key):
    """Vignere cipher, plaintext is in bytes and key is a string"""
    m = tuple(ord(k) for k in key)
    M = len(key)
    return bytes((t + m[i%M]) % 256 for i, t in enumerate(plaintext))

def decrypt_bytes(crypted, key):
    """Reversed Vignere cipher, plaintext is in bytes and key is a string"""
    m = tuple((-ord(k))%256 for k in key)
    M = len(key)
    return bytes((t + m[i%M]) % 256 for i, t in enumerate(crypted))

def string_to_ints(string):
    """From string to concatenated string of its binary values"""
    res = bytes(string, encoding='utf-8')
    return ''.join(map(lambda x: str(int(x)).zfill(3), res))

def ints_to_string(ints):
    """From concatenated string of binary values to string"""
    loi = [int(ints[i:i+3]) for i in range(0, len(ints), 3)]
    return str(bytes(loi), encoding='utf-8')

def hash_key(key):
    return hashlib.sha256(bytes(key, encoding='utf-8')).hexdigest()

