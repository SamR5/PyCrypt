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
    data["key"] = hashedKey
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

def encrypt_bytes_py(plaintext, key):
    """Vignere cipher, plaintext is in bytes and key is a string"""
    m = tuple(ord(k) for k in key)
    M = len(key)
    return bytes((t + m[i%M]) % 256 for i, t in enumerate(plaintext))

def decrypt_bytes_py(crypted, key):
    """Reversed Vignere cipher, crypted is in bytes and key is a string"""
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

############################
# https://stackoverflow.com/questions/14887378/how-to-return-array-from-c-function-to-python-using-ctypes
import ctypes
from numpy.ctypeslib import ndpointer
import timeit

clibFound = False
try:
    lib = ctypes.CDLL("./cryu.so")
    lib.encrypt.argtypes = [ctypes.c_char_p, ctypes.c_long, ctypes.c_char_p]
    lib.decrypt.argtypes = [ctypes.c_char_p, ctypes.c_long, ctypes.c_char_p]

    def encrypt_bytes_c(plaintext, key):
        """plaintext is in bytes and key is str"""
        lib.encrypt.restype = ndpointer(dtype=ctypes.c_int,
                                        shape=(len(plaintext),))
        result = lib.encrypt(ctypes.c_char_p(plaintext), len(plaintext),
                             ctypes.c_char_p(key.encode('utf-8')))
        return bytes(tuple(result))

    def decrypt_bytes_c(plaintext, key):
        """plaintext is in bytes and key is str"""
        global result
        lib.decrypt.restype = ndpointer(dtype=ctypes.c_int,
                                        shape=(len(plaintext),))
        result = lib.decrypt(ctypes.c_char_p(plaintext), len(plaintext),
                             ctypes.c_char_p(key.encode('utf-8')))
        return bytes(tuple(result))
    clibFound = True
except:
    clibFound = False

if clibFound:
    encrypt_bytes = encrypt_bytes_c
    decrypt_bytes = decrypt_bytes_c
else:
    encrypt_bytes = encrypt_bytes_py
    decrypt_bytes = decrypt_bytes_py

pt = b"AZERTYazerty"*1000
ky = "1234"*10

def test_speed(r=5, n=100):
    pye = timeit.repeat(stmt='encrypt_bytes_py(pt, ky)',
                        setup="from __main__ import encrypt_bytes_py, pt, ky",
                        repeat=r, number=n)
    pyd = timeit.repeat(stmt='decrypt_bytes_py(pt, ky)',
                        setup="from __main__ import decrypt_bytes_py, pt, ky",
                        repeat=r, number=n)
    ce = timeit.repeat(stmt='encrypt_bytes_c(pt, ky)',
                       setup="from __main__ import encrypt_bytes_c, pt, ky",
                       repeat=r, number=n)
    cd = timeit.repeat(stmt='decrypt_bytes_c(pt, ky)',
                       setup="from __main__ import decrypt_bytes_c, pt, ky",
                       repeat=r, number=n)
    pye, pyd, ce, cd = min(pye), min(pyd), min(ce), min(cd)
    print(f"With the C library, encryption speed is {pye/ce:.2f} faster")
    print(f"With the C library, decryption speed is {pyd/cd:.2f} faster")


