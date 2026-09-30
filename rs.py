"""Part 2 - Reed-Solomon error correction: bytes as polynomials over GF(256)."""

EXP, LOG = [0] * 512, [0] * 256
x = 1
for i in range(255):              # powers of 2, wrapping around at 256
    EXP[i], LOG[x] = x, i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D                # x^8 + x^4 + x^3 + x^2 + 1
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]


def generator(n):
    """(x - 2^0)(x - 2^1)...(x - 2^(n-1)), highest power first."""
    g = [1]
    for i in range(n):
        g = [a ^ mul(b, EXP[i]) for a, b in zip(g + [0], [0] + g)]
    return g


def ec_codewords(data, n):
    """The remainder of data * x^n divided by the generator: n error-correction bytes."""
    g = generator(n)
    rem = list(data) + [0] * n
    for i in range(len(data)):
        c = rem[i]
        if c:
            for j in range(1, n + 1):
                rem[i + j] ^= mul(g[j], c)
    return rem[len(data):]
