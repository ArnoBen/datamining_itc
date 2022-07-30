import pickle
from hashlib import md5


def hash_tuple(t):
    bytez = pickle.dumps(t)
    hashed = md5(bytez)
    return hashed.hexdigest()