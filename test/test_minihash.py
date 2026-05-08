from datasketch import MinHash


def shingles(text, k=3):
    text = text.lower()
    return {
        text[i : i + k]
        for i in range(len(text) - k + 1)
    }


def build_minhash(texts, num_perm=128):
    m = MinHash(num_perm=num_perm)

    if isinstance(texts, str):
        texts = [texts]

    for text in texts:
        for s in shingles(text):
            m.update(s.encode("utf-8"))

    return m


m1 = build_minhash(["hello world", "see you"])