import numpy as np
import hashlib

def hasharray(arr):
    return hash(hashlib.sha1(np.array(arr)).hexdigest())

def hashcombine(*xs):
    k = 0
    for x in xs:
        k ^= hash(x)
    k ^= hash(xs)
    return k


