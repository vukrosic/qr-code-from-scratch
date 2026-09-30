"""Part 1 - turn text into the data codewords of a QR code (byte mode)."""


def to_bits(value, width):
    return [(value >> i) & 1 for i in range(width - 1, -1, -1)]


def encode(text, capacity):
    """capacity = number of data codewords (bytes) this version and level hold."""
    data = text.encode('utf-8')
    bits = to_bits(0b0100, 4)                     # mode: byte
    bits += to_bits(len(data), 8)                 # how many bytes follow
    for b in data:
        bits += to_bits(b, 8)                     # the bytes themselves
    room = capacity * 8
    assert len(bits) <= room, 'text too long for this version'
    bits += [0] * min(4, room - len(bits))        # terminator
    bits += [0] * (-len(bits) % 8)                # fill the last byte
    words = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = [0b11101100, 0b00010001]
    while len(words) < capacity:
        words.append(pad[(len(words) - len(bits) // 8) % 2])   # fill the rest
    return words
