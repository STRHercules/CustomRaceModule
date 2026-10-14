"""PKWARE DCL ``explode`` decompression used by some WotLK MPQ sectors.

Ported from EsteriaWoW's dependency-free client tooling. Most 3.3.5a archives
use zlib, but community MPQs can contain PKWARE-compressed sectors.
"""

from __future__ import annotations

_LIT_LEN = bytes([
    11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8,
    9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5,
    7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
    8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8, 7, 24, 10, 27,
    44, 253, 253, 253, 252, 252, 252, 13, 12, 45, 12, 45, 12, 61, 12, 45,
    44, 173,
])
_LEN_LEN = bytes([2, 35, 36, 53, 38, 23])
_DIST_LEN = bytes([2, 20, 53, 230, 247, 151, 248])
_BASE = (3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264)
_EXTRA = (0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8)


class _Huffman:
    __slots__ = ("count", "symbol")

    def __init__(self, rep: bytes):
        lengths = []
        for packed in rep:
            repeat = (packed >> 4) + 1
            lengths.extend([packed & 15] * repeat)
        count = [0] * 17
        for length in lengths:
            count[length] += 1
        offsets = [0] * 17
        for length in range(1, 16):
            offsets[length + 1] = offsets[length] + count[length]
        symbol = [0] * len(lengths)
        for index, length in enumerate(lengths):
            if length:
                symbol[offsets[length]] = index
                offsets[length] += 1
        self.count = count
        self.symbol = symbol


_LIT_CODE = _Huffman(_LIT_LEN)
_LEN_CODE = _Huffman(_LEN_LEN)
_DIST_CODE = _Huffman(_DIST_LEN)


class _BitStream:
    __slots__ = ("data", "pos", "bitbuf", "bitcnt")

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.bitbuf = 0
        self.bitcnt = 0

    def bits(self, need: int) -> int:
        value = self.bitbuf
        while self.bitcnt < need:
            if self.pos >= len(self.data):
                raise ValueError("PKWARE stream ended mid-symbol")
            value |= self.data[self.pos] << self.bitcnt
            self.pos += 1
            self.bitcnt += 8
        self.bitbuf = value >> need
        self.bitcnt -= need
        return value & ((1 << need) - 1)

    def decode(self, huff: _Huffman) -> int:
        code = 0
        first = 0
        index = 0
        for length in range(1, 17):
            code |= self.bits(1)
            count = huff.count[length]
            if code - first < count:
                return huff.symbol[index + (code - first)]
            index += count
            first = (first + count) << 1
            code <<= 1
        raise ValueError("invalid PKWARE Huffman code")


def explode(data: bytes, expected_size: int = -1) -> bytes:
    """Decompress one PKWARE DCL stream."""
    if len(data) < 4:
        raise ValueError("PKWARE stream too short")
    literal_mode = data[0]
    dict_bits = data[1]
    if literal_mode not in (0, 1):
        raise ValueError("bad PKWARE literal mode %d" % literal_mode)
    if not 4 <= dict_bits <= 6:
        raise ValueError("bad PKWARE dictionary size %d" % dict_bits)

    stream = _BitStream(data[2:])
    output = bytearray()
    while True:
        if stream.bits(1):
            symbol = stream.decode(_LEN_CODE)
            length = _BASE[symbol] + stream.bits(_EXTRA[symbol])
            if length == 519:
                break
            shift = 2 if length == 2 else dict_bits
            distance = stream.decode(_DIST_CODE) << shift
            distance += stream.bits(shift)
            distance += 1
            if distance > len(output):
                raise ValueError("PKWARE back-reference before start of output")
            start = len(output) - distance
            for index in range(length):
                output.append(output[start + index])
        elif literal_mode:
            output.append(stream.decode(_LIT_CODE))
        else:
            output.append(stream.bits(8))
        if 0 <= expected_size <= len(output):
            break
    return bytes(output)
