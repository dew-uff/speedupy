"""Reference values of the two native hashes.

Produced by the original liba5hash.so and libmuseair.so, built on Linux x86_64
from the commits pinned in native/NOTICE, and published as the
test vectors of the speedupy-native 0.1.0 package (tests/test_vectors.py).
Every binary of native/lib/ must reproduce them on its own platform: the hash
tests check them through the hash classes, and native/check.py checks them
right after the build. They change only when a submodule moves
(native/README.md, "Moving a submodule").

Plain data, no import of SpeeduPy: native/check.py loads this file by path.
"""

import hashlib

INPUTS = {
    "empty": b"",
    "one_byte": b"a",
    "abc": b"abc",
    "ascii_sentence": b"The quick brown fox jumps over the lazy dog",
    "utf8": b"memoiza\xc3\xa7\xc3\xa3o de fun\xc3\xa7\xc3\xb5es puras",
    "nul_bytes": b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    "all_bytes": b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff",
    "kib_1": hashlib.sha256(b"speedupy-1KiB").digest() * 32,
    "kib_64": hashlib.sha256(b"speedupy-64KiB").digest() * 2048,
    "mib_1": hashlib.sha256(b"speedupy-1MiB").digest() * 32768,
}

A5HASH = {  # (input, seed): a5hash_128_64
    ("empty", 0): 0x0F2D4F1152E2FD91,
    ("empty", 1): 0x20EE8AA6F7A8D8DA,
    ("empty", 3735928559): 0xF3C70EE863E34586,
    ("empty", 18446744073709551615): 0xDB342473DEB309E3,
    ("one_byte", 0): 0xC9424D6FE845B90E,
    ("one_byte", 1): 0xC522354A93B0810F,
    ("one_byte", 3735928559): 0x30FBFA8EDB671FE5,
    ("one_byte", 18446744073709551615): 0x7CF7C98D52D42F58,
    ("abc", 0): 0xCF9C53265409B54F,
    ("abc", 1): 0x9E72D05150C6B601,
    ("abc", 3735928559): 0xD1ADF443D23A6847,
    ("abc", 18446744073709551615): 0xA0EE34CB6D251835,
    ("ascii_sentence", 0): 0xA2D7775B627EE6C0,
    ("ascii_sentence", 1): 0xBBEF21CF04F07E1D,
    ("ascii_sentence", 3735928559): 0xFD0B9D976792733F,
    ("ascii_sentence", 18446744073709551615): 0xAB04CFA002672EE0,
    ("utf8", 0): 0xCA95B36CF3A4BCC1,
    ("utf8", 1): 0x339B0FFD35C3BA5D,
    ("utf8", 3735928559): 0x7F51CA69DC81C503,
    ("utf8", 18446744073709551615): 0xE9C2739F8A0C906D,
    ("nul_bytes", 0): 0x72C53D9414ED7A00,
    ("nul_bytes", 1): 0xD8A0E0E51405BE8D,
    ("nul_bytes", 3735928559): 0x574F9D41BEA2FCCD,
    ("nul_bytes", 18446744073709551615): 0x25414D163082DC3B,
    ("all_bytes", 0): 0x389D24736FC07578,
    ("all_bytes", 1): 0x8ABCCACE6DB9F991,
    ("all_bytes", 3735928559): 0x7795CCC4C5855242,
    ("all_bytes", 18446744073709551615): 0x92BEE003D1AD20B1,
    ("kib_1", 0): 0xE1B7DA7BFFC215FC,
    ("kib_1", 1): 0x81F5365BBE6DA37F,
    ("kib_1", 3735928559): 0xDCAD31EFDA10A996,
    ("kib_1", 18446744073709551615): 0xE0E3A223C7884D55,
    ("kib_64", 0): 0xFF2A5DF0A816BC40,
    ("kib_64", 1): 0xBEB9331AE0C8DE1D,
    ("kib_64", 3735928559): 0xC342A68B09494971,
    ("kib_64", 18446744073709551615): 0x8B6B4A91D2B47967,
    ("mib_1", 0): 0x7ECA87926A4E6DC9,
    ("mib_1", 1): 0x96F507293B359527,
    ("mib_1", 3735928559): 0x4319477A63D27474,
    ("mib_1", 18446744073709551615): 0xA985757EB3897D8B,
}

MUSEAIR = {  # (input, seed): museair_bfast_64
    ("empty", 0): 0xBFEEF88760757234,
    ("empty", 1): 0x63ED0D8EF92AC2C7,
    ("empty", 3735928559): 0xC80930C5F1956790,
    ("empty", 18446744073709551615): 0x3F604E4A122669EE,
    ("one_byte", 0): 0xAA41B83C5EAFB659,
    ("one_byte", 1): 0x6FCBCC536C67532B,
    ("one_byte", 3735928559): 0x8B37314CF4F81989,
    ("one_byte", 18446744073709551615): 0x0162DDC5EFC5E496,
    ("abc", 0): 0x8525EB65D3B5FF99,
    ("abc", 1): 0xF3DD781813B311BB,
    ("abc", 3735928559): 0xADBA165C8C809960,
    ("abc", 18446744073709551615): 0x84855F241C64F5E8,
    ("ascii_sentence", 0): 0xF8912CB64FF4768F,
    ("ascii_sentence", 1): 0x047C8E332D508B4E,
    ("ascii_sentence", 3735928559): 0x9058580C7E1CC0F3,
    ("ascii_sentence", 18446744073709551615): 0xFFDD5D5320FE1518,
    ("utf8", 0): 0x0DD89EC81F2CB1E2,
    ("utf8", 1): 0x8120782B740FFEC5,
    ("utf8", 3735928559): 0x40C3A7AA8A9844CB,
    ("utf8", 18446744073709551615): 0xC100D6A4E57EE6EE,
    ("nul_bytes", 0): 0xBA45B90E86609330,
    ("nul_bytes", 1): 0xE0E5FDDC3C26896D,
    ("nul_bytes", 3735928559): 0x6705313693F4B587,
    ("nul_bytes", 18446744073709551615): 0x642531EA1C7F9BF9,
    ("all_bytes", 0): 0x77C402ACC4A638EA,
    ("all_bytes", 1): 0xEE47664AB47EF67D,
    ("all_bytes", 3735928559): 0xD391BA1B28B24DD8,
    ("all_bytes", 18446744073709551615): 0xC31379CE5DB03472,
    ("kib_1", 0): 0xE743EE60C07BFB2A,
    ("kib_1", 1): 0xF1C5828A77FAC37E,
    ("kib_1", 3735928559): 0x7DD609530F894D8C,
    ("kib_1", 18446744073709551615): 0xEE2DE55454159E42,
    ("kib_64", 0): 0x39C5E07F81E9A7BF,
    ("kib_64", 1): 0xF9B2AD5D5652A249,
    ("kib_64", 3735928559): 0x3220E8B54D25BED4,
    ("kib_64", 18446744073709551615): 0x5948071BD68050E8,
    ("mib_1", 0): 0x94395DE029EDE7D7,
    ("mib_1", 1): 0xB9B5ECF57CE783B6,
    ("mib_1", 3735928559): 0xB00CF347BABA92EB,
    ("mib_1", 18446744073709551615): 0xC395C7E855426CB3,
}
