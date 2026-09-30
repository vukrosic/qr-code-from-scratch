"""Part 4 - masks break up bad patterns; the format strip says which mask and level."""

MASKS = [
    lambda x, y: (x + y) % 2 == 0,
    lambda x, y: y % 2 == 0,
    lambda x, y: x % 3 == 0,
    lambda x, y: (x + y) % 3 == 0,
    lambda x, y: (x // 3 + y // 2) % 2 == 0,
    lambda x, y: x * y % 2 + x * y % 3 == 0,
    lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
    lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
]
LEVEL = {'L': 0b01, 'M': 0b00, 'Q': 0b11, 'H': 0b10}


def apply(grid, fixed, m):
    return [[v ^ (not fixed[y][x] and MASKS[m](x, y)) for x, v in enumerate(row)]
            for y, row in enumerate(grid)]


def penalty(grid):
    n = len(grid)
    lines = grid + [list(col) for col in zip(*grid)]          # rows, then columns
    runs = 0
    for line in lines:                                        # 1: five or more in a row
        count = 1
        for a, b in zip(line, line[1:] + [None]):
            if a == b:
                count += 1
            else:
                runs += count - 2 if count >= 5 else 0
                count = 1
    boxes = 3 * sum(grid[y][x] == grid[y][x + 1] == grid[y + 1][x] == grid[y + 1][x + 1]
                    for y in range(n - 1) for x in range(n - 1))   # 2: 2x2 blocks
    fakes = 0
    for line in lines:                                        # 3: look-alike finders
        s = ''.join(map(str, line))
        for p in ('10111010000', '00001011101'):
            fakes += 40 * sum(s.startswith(p, i) for i in range(n - 10))
    dark = sum(map(sum, grid)) * 100 / (n * n)
    balance = 10 * int(abs(dark - 50) // 5)                   # 4: too dark or too light
    return [runs, boxes, fakes, balance]


def format_bits(level, m):
    data = LEVEL[level] << 3 | m
    rem = data
    for _ in range(10):                   # BCH code: 10 check bits
        rem = (rem << 1) ^ ((rem >> 9) * 0x537)
    return (data << 10 | rem) ^ 0b101010000010010


def draw_format(grid, bits):
    n = len(grid)
    b = [(bits >> i) & 1 for i in range(15)]
    first = [(8, i) for i in range(6)] + [(8, 7), (8, 8), (7, 8)] + [(14 - i, 8) for i in range(9, 15)]
    second = [(n - 1 - i, 8) for i in range(8)] + [(8, n - 15 + i) for i in range(8, 15)]
    for (x, y), v in zip(first, b):
        grid[y][x] = v
    for (x, y), v in zip(second, b):
        grid[y][x] = v
    return first, second
