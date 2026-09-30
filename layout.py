"""Part 3 - the grid: fixed patterns first, then data bits in a zigzag."""


def blank(version):
    size = 17 + 4 * version
    grid = [[0] * size for _ in range(size)]       # 1 = dark
    fixed = [[False] * size for _ in range(size)]  # True = not for data

    def put(x, y, dark):
        if 0 <= x < size and 0 <= y < size:
            grid[y][x], fixed[y][x] = int(dark), True

    for i in range(size):                          # timing lines
        put(6, i, i % 2 == 0)
        put(i, 6, i % 2 == 0)
    for cx, cy in [(3, 3), (size - 4, 3), (3, size - 4)]:   # finder patterns
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                put(cx + dx, cy + dy, max(abs(dx), abs(dy)) not in (2, 4))
    if version >= 2:                               # alignment pattern
        c = size - 7
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                put(c + dx, c + dy, max(abs(dx), abs(dy)) != 1)
    for i in range(9):                             # reserve the format strips
        if i != 6:
            put(8, i, 0)
            put(i, 8, 0)
    for i in range(8):
        put(size - 1 - i, 8, 0)
        put(8, size - 1 - i, 0)
    put(8, size - 8, 1)                            # the dark module
    return grid, fixed


def zigzag(size, fixed):
    """Data cells in placement order: two columns at a time, up then down."""
    order, right = [], size - 1
    while right >= 1:
        if right == 6:
            right = 5                              # skip the timing column
        for vert in range(size):
            y = size - 1 - vert if (right + 1) & 2 == 0 else vert
            for x in (right, right - 1):
                if not fixed[y][x]:
                    order.append((x, y))
        right -= 2
    return order


def place(grid, fixed, codewords):
    bits = [(w >> (7 - i)) & 1 for w in codewords for i in range(8)]
    order = zigzag(len(grid), fixed)
    for (x, y), b in zip(order, bits):
        grid[y][x] = b
    return order
