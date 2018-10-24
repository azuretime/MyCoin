#Question 1

import hashlib
m = hashlib.sha256()
m.update(b"Blockchain Technology")
print(m.hexdigest())

m = hashlib.sha512()
m.update(b"Blockchain Technology")
print(m.hexdigest())

m = hashlib.sha3_256()
m.update(b"Blockchain Technology")
print(m.hexdigest())

m = hashlib.sha3_512()
m.update(b"Blockchain Technology")
print(m.hexdigest())

m = hashlib.sha3_512()
m.update(b"Blockchain Technology")
print(m.hexdigest())

#Question 2

def H(n,msg):

    m = hashlib.sha256()
    m.update(msg.encode('utf-8'))
    return m.digest()[:int(n/8)]

import string
from random import *
def randomstr():
    min_char = 8
    max_char = 12
    allchar =  string.digits #+ string.punctuation + string.ascii_letters
    return "".join(choice(allchar) for x in range(randint(min_char, max_char)))

def time_collision(n):
    collision = False
    while not collision:
        m1 = randomstr()
        m2 = randomstr()
        if H(n,m1) == H(n,m2):
            collision = True

import time
start = time.time()
time_collision(8)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_collision(16)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_collision(24)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_collision(32)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_collision(40)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))


def time_preimage(n):
    found = False
    while not found:
        h = H(n, randomstr())
        #print(h,b'\x00'*int(n/8))

        if h == b'\x00'*int(n/8):
            found = True

start = time.time()
time_preimage(8)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_preimage(16)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_preimage(24)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_preimage(32)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

start = time.time()
time_preimage(40)
elapsed = time.time() - start
print("Time taken: {}s".format(elapsed))

#  Question 3

import ecdsa

sk = ecdsa.SigningKey.generate() #curve=ecdsa.NIST192p Private key
vk = sk.get_verifying_key() # Public Key
sig = sk.sign(b"Blockchain Technology")
vk.verify(sig, b"Blockchain Technology")

