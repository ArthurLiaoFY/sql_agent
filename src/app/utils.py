import numpy as np
from datasketch import MinHash


def serialize_minhash(m: MinHash):
    return m.hashvalues.tolist()


def deserialize_minhash(values):
    m = MinHash(num_perm=len(values))
    m.hashvalues = np.array(values, dtype=np.uint64)
    return m
