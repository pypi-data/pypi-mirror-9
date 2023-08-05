import numpy as np
import hashlib

def hasharray(arr):
    return hash(hashlib.sha1(np.ascontiguousarray(arr)).hexdigest())

def hashcombine(*xs):
    k = 0
    for x in xs:
        k ^= hash(x)
    k ^= hash(xs)
    return k

def hashdict(d):
    k = 0
    for key,val in d.iteritems():
        k ^= hash(key) ^ hash(val)
    return k
