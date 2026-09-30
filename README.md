# QR codes from scratch

This repo builds a QR code generator in 259 lines of plain Python, with no libraries. It turns text into a scannable PNG in the same five steps every QR code goes through:

| Part | File | Lines | What it does |
| --- | --- | --- | --- |
| 1. Encode | `encode.py` | 23 | Writes the byte-mode header (mode `0100` and the length), then 8 bits per byte, a terminator and pad bytes `236`/`17`. |
| 2. Error correction | `rs.py` | 35 | Reed–Solomon over GF(256) with polynomial `0x11D`: builds the generator and computes the check bytes. |
| 3. Place | `layout.py` | 56 | Draws the fixed patterns (finders, separators, timing lines, alignment, dark module), then snakes the data bits up and down 2-column strips from the bottom-right corner. |
| 4. Mask | `mask.py` | 62 | Tries all 8 masks, scores each with the 4 penalty rules, and writes the 15-bit format strip twice. |
| 5. Put it together | `qr.py` | 83 | Picks the smallest version (1–6) that fits, splits data into blocks, interleaves them, keeps the cheapest mask and saves a PNG using `zlib`. |

`demo.py` runs every part on `"hello, world"`, reads the results back with OpenCV, damages codes on purpose and measures how big a logo can be.

This is the companion code for the "QR codes from scratch" course on [Vuk Rosić’s YouTube channel](https://www.youtube.com/@vukrosic).

## Run it

`qr.py` needs only Python 3:

```bash
python3 qr.py "hello, world"
```

It prints the code in the terminal and writes `qr.png`. Scan it with your phone.

The demo also needs OpenCV and numpy (tested with opencv-python 4.13.0 and numpy 2.2.5):

```bash
pip install opencv-python numpy
python3 demo.py
```

## Results in the video

These were measured on an Apple M4 MacBook. The full log is in [`results/demo-output.txt`](results/demo-output.txt).

- `"hello, world"` at level M is version 1 (21 × 21): 16 data bytes + 10 check bytes = 26 codewords. 233 of the 441 modules are fixed and 208 hold data.
- Mask 0 scores 319 penalty points, the lowest of the 8. The unmasked grid scores 460.
- The format bits for level M, mask 0 are `101010000010010`.
- The link to this repo is version 4 (33 × 33) with mask 2. It is built in 7.9 ms, and OpenCV reads it back.
- Damage: with 0–5 of the 26 codewords flipped, OpenCV reads 20/20 codes. With 6–8 flipped, it reads 0/20. Ten check bytes repair five bad bytes.
- Largest blank square in the middle (a "logo") that still reads, for the repo link:

| Level | Version | Largest square | Share of the code |
| --- | --- | --- | --- |
| L | 3 (29 × 29) | 6 × 6 | 4% |
| M | 4 (33 × 33) | 10 × 10 | 9% |
| Q | 5 (37 × 37) | 14 × 14 | 14% |
| H | 6 (41 × 41) | 18 × 18 | 19% |

The output matches python-qrcode 8.2 on all 1,352 matrices for versions 1–6, levels L/M/Q/H and all 8 masks.

## Try it yourself

1. **Alphanumeric mode.** Digits, capital letters and `$%*+-./: ` (space) fit in 11 bits per pair of characters instead of 16. Add mode `0010` to `encode.py`: use a 9-bit length, encode each pair as `45 × a + b` in 11 bits, and put a final single character in 6 bits. Compare the version for `HTTPS://EXAMPLE.COM` in both modes.
2. **Bigger codes.** `qr.py` stops at version 6. Extend `EC_TABLE` and the alignment positions in `layout.py`. From version 7, also draw the two 18-bit version blocks. Then encode a 200-character paragraph.
3. **Write the reader.** Go picture in, text out: find the three finders, sample the grid, read the format strip, undo the mask, walk the zigzag, de-interleave and decode. Start with the clean `qr.png` from `qr.py`, where each module is exactly 10 pixels.

## What real QR libraries add

They support versions 1–40, numeric and kanji modes, and mixed segments that switch mode mid-text to save bits. Readers add perspective correction, alignment-pattern tracking and full Reed–Solomon erasure decoding. The five steps are the same. The standard is ISO/IEC 18004.

MIT License.
