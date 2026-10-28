#!/usr/bin/env python3
"""cps2fix - builds the fixed CPS2 versions of Cadillacs & Dinosaurs and The Punisher from the original CPS1 ROM sets.

You supply the original MAME zips (roms/), the tool checks every file by CRC32 before it does anything, builds
the CPS2 files and writes a MAME set and a Darksoft set per game. See README.md.

usage: python3 cps2fix.py [--roms DIR] [--out DIR] [--game dino|punisher|all] [--no-mame] [--no-darksoft] [--check]
Python 3.6 or newer, standard library only.

Licensed under the GNU General Public License v3.0 (see LICENSE)."""
import argparse
import hashlib
import json
import os
import struct
import sys
import time
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SW = 0x80000          # size of one 68000 ROM file

# --------------------------------------------------------------------------------------------------------------------
# The original CPS1 files each game is built from: (name in the MAME set, size, CRC32, set it comes from)
# --------------------------------------------------------------------------------------------------------------------
DINO_FILES = [
    ("cdu_23a.8f", 0x80000, 0x7c2543cd, "dinou"), ("cdu_22a.7f", 0x80000, 0xd19f981e, "dinou"),
    ("cde_21a.6f", 0x80000, 0x66d23de2, "dino"),
    ("cd-1m.3a", 0x80000, 0x8da4f917, "dino"), ("cd-3m.5a", 0x80000, 0x6c40f603, "dino"),
    ("cd-2m.4a", 0x80000, 0x09c8fc2d, "dino"), ("cd-4m.6a", 0x80000, 0x637ff38f, "dino"),
    ("cd-5m.7a", 0x80000, 0x470befee, "dino"), ("cd-7m.9a", 0x80000, 0x22bfb7a3, "dino"),
    ("cd-6m.8a", 0x80000, 0xe7599ac4, "dino"), ("cd-8m.10a", 0x80000, 0x211b4b15, "dino"),
    ("cd_q.5k", 0x20000, 0x605fdb0b, "dino"),
    ("cd-q1.1k", 0x80000, 0x60927775, "dino"), ("cd-q2.2k", 0x80000, 0x770f4c47, "dino"),
    ("cd-q3.3k", 0x80000, 0x2f273ffc, "dino"), ("cd-q4.4k", 0x80000, 0x2c67821d, "dino"),
]
PUNI_FILES = [
    ("psu_26.11e", 0x20000, 0x9236d121, "punisheru"), ("psu_30.11f", 0x20000, 0x8320e501, "punisheru"),
    ("psu_27.12e", 0x20000, 0x61c960a1, "punisheru"), ("psu_31.12f", 0x20000, 0x78d4c298, "punisheru"),
    ("psu_24.9e", 0x20000, 0x1cfecad7, "punisheru"), ("psu_28.9f", 0x20000, 0xbdf921c1, "punisheru"),
    ("psu_25.10e", 0x20000, 0xc51acc94, "punisheru"), ("psu_29.10f", 0x20000, 0x52dce1ca, "punisheru"),
    ("ps_21.6f", 0x80000, 0x8affa5a9, "punisher"),
    ("ps-1m.3a", 0x80000, 0x77b7ccab, "punisher"), ("ps-3m.5a", 0x80000, 0x0122720b, "punisher"),
    ("ps-2m.4a", 0x80000, 0x64fa58d4, "punisher"), ("ps-4m.6a", 0x80000, 0x60da42c8, "punisher"),
    ("ps-5m.7a", 0x80000, 0xc54ea839, "punisher"), ("ps-7m.9a", 0x80000, 0x04c5acbd, "punisher"),
    ("ps-6m.8a", 0x80000, 0xa544f4cc, "punisher"), ("ps-8m.10a", 0x80000, 0x8f02f436, "punisher"),
    ("ps_q.5k", 0x20000, 0x49ff4446, "punisher"),
    ("ps-q1.1k", 0x80000, 0x31fd8726, "punisher"), ("ps-q2.2k", 0x80000, 0x980a9eef, "punisher"),
    ("ps-q3.3k", 0x80000, 0x0dd44491, "punisher"), ("ps-q4.4k", 0x80000, 0xbed42f03, "punisher"),
]
# 68000 code of the other regional sets: recognised (and reported) but not converted, see README.md
OTHER_SETS = [
    ("dino", "Cadillacs: Kyouryuu-Shin Seiki (World 930201)", [0x8f4e585e, 0x9278aa12, 0x66d23de2]),
    ("dinoa", "Cadillacs: Kyouryuu-Shin Seiki (Asia 930201)", [0xf477f7a0, 0x1e534ca5, 0x74b04329]),
    ("dinou", "Cadillacs and Dinosaurs (USA 930201)", [0x7c2543cd, 0xd19f981e, 0x66d23de2]),
    ("punisher", "The Punisher (World 930422)", [0x389a99d2, 0x68fb06ac, 0x3eb181c3, 0x37108e7b]),
    ("punisherj", "The Punisher (Japan 930422)", [0x6b2fda52, 0xe01036bc]),
    ("punisheru", "The Punisher (USA 930422)", [0x9236d121, 0x8320e501, 0x61c960a1, 0x78d4c298]),
]


def crc32(b):
    return zlib.crc32(b) & 0xffffffff


# --------------------------------------------------------------------------------------------------------------------
# finding the original files: every zip in the roms folder (and loose files) is indexed by CRC32
# --------------------------------------------------------------------------------------------------------------------
class RomIndex:
    def __init__(self, folder):
        self.by_crc = {}          # (crc, size) -> (zip path or file path, member name or None)
        self.by_name = {}         # file name -> list of (crc, size, where)
        self.zips = []
        self.found_sets = {}
        for dirpath, _dirs, files in os.walk(folder):
            for fn in sorted(files):
                path = os.path.join(dirpath, fn)
                if fn.lower().endswith(".zip"):
                    try:
                        z = zipfile.ZipFile(path)
                    except zipfile.BadZipFile:
                        print("  warning: %s is not a valid zip file, skipped" % path)
                        continue
                    self.zips.append(fn)
                    for zi in z.infolist():
                        if zi.is_dir():
                            continue
                        self._add(zi.CRC, zi.file_size, path, zi.filename)
                    z.close()
                elif ":" not in fn and not fn.lower().endswith((".md", ".txt", ".identifier")):
                    try:
                        size = os.path.getsize(path)
                        if size in (0x80000, 0x20000):
                            with open(path, "rb") as f:
                                self._add(crc32(f.read()), size, path, None)
                    except OSError:
                        pass

    def _add(self, crc, size, path, member):
        self.by_crc.setdefault((crc, size), (path, member))
        name = os.path.basename(member or path)
        self.by_name.setdefault(name, []).append((crc, size, path))

    def read(self, crc, size):
        path, member = self.by_crc[(crc, size)]
        if member is None:
            with open(path, "rb") as f:
                return f.read()
        with zipfile.ZipFile(path) as z:
            return z.read(member)

    def has(self, crc, size):
        return (crc, size) in self.by_crc


def check_inputs(index, files):
    """report every file a game needs; returns (ok, {name: data})"""
    ok, data = True, {}
    for name, size, crc, owner in files:
        if index.has(crc, size):
            print("    ok       %-12s %7d  %08x  (%s)" % (name, size, crc, os.path.basename(index.by_crc[(crc, size)][0])))
            data[name] = None
        else:
            ok = False
            wrong = [w for w in index.by_name.get(name, [])]
            if wrong:
                print("    WRONG    %-12s expected %08x, %s has %08x" % (name, crc, os.path.basename(wrong[0][2]), wrong[0][0]))
            else:
                print("    MISSING  %-12s %7d  %08x  (from %s.zip)" % (name, size, crc, owner))
    return ok


def load(index, files):
    return {name: index.read(crc, size) for name, size, crc, _o in files}


# --------------------------------------------------------------------------------------------------------------------
# helpers shared by both games
# --------------------------------------------------------------------------------------------------------------------
def swap16(b):
    """swap the two bytes of every 16-bit word"""
    b = bytearray(b)
    b[0::2], b[1::2] = b[1::2], b[0::2]
    return bytes(b)


def samples(files, names):
    """CPS2 QSound samples: the four CPS1 sample files with every word swapped, twice (4 MB)"""
    s = swap16(b"".join(files[n] for n in names))
    assert len(s) == 0x200000
    return s + s


def cps1_graphics(files, order):
    """the 4 MB graphics region as MAME loads it (ROM_LOAD64_WORD: four files side by side per 2 MB)"""
    g = bytearray(0x400000)
    for (name, base, word) in order:
        d = files[name]
        g[base + word:base + 0x200000:8] = d[0::2]
        g[base + word + 1:base + 0x200000:8] = d[1::2]
    return g


GFX_ORDER = [("1m", 0x000000, 0), ("3m", 0x000000, 2), ("2m", 0x000000, 4), ("4m", 0x000000, 6),
             ("5m", 0x200000, 0), ("7m", 0x200000, 2), ("6m", 0x200000, 4), ("8m", 0x200000, 6)]
BANK = 0x200000 // 8      # 64-bit words per 2 MB bank


def unshuffle_perm(n):
    """MAME cps2_gfx_decode: decoded[i] = raw[perm[i]] for the words of one bank"""
    def rec(buf, lo, ln):
        if ln == 2:
            return
        ln //= 2
        rec(buf, lo, ln)
        rec(buf, lo + ln, ln)
        for i in range(ln // 2):
            buf[lo + ln // 2 + i], buf[lo + ln + i] = buf[lo + ln + i], buf[lo + ln // 2 + i]
    buf = list(range(n))
    rec(buf, 0, n)
    return buf


_PERM = []


def perm():
    if not _PERM:
        _PERM.append(unshuffle_perm(BANK))
    return _PERM[0]


def region_to_files(dec):
    """decoded 16 MB region -> shuffled raw words -> the four 4 MB graphics files (13m 15m 17m 19m)"""
    p = perm()
    raw = bytearray(len(dec))
    for bank in range(len(dec) // (BANK * 8)):
        b = bank * BANK * 8
        for i in range(BANK):
            o = b + p[i] * 8
            raw[o:o + 8] = dec[b + i * 8:b + i * 8 + 8]
    return raw_to_files(raw)


def raw_to_files(raw):
    out = []
    for k in range(4):
        f = bytearray(0x400000)
        f[0::2] = raw[2 * k::8]
        f[1::2] = raw[2 * k + 1::8]
        out.append(f)
    return out


def files_to_raw(files):
    raw = bytearray(0x1000000)
    for k in range(4):
        raw[2 * k::8] = files[k][0::2]
        raw[2 * k + 1::8] = files[k][1::2]
    return raw


# --- pen mask baking: a copy of a 16x16 tile in which the pens that are not in the CPS-B pen mask are the transparent pen 15 ---
_ROWCACHE = {}


def baked_row(row, mask):
    key = (row, mask)
    r = _ROWCACHE.get(key)
    if r is None:
        pens = []
        for half in (0, 1):
            c = row[half * 4:half * 4 + 4]
            for x in range(8):
                pen = 0
                for j, byte in enumerate((3, 2, 1, 0)):
                    pen |= ((c[byte] >> (7 - x)) & 1) << (3 - j)
                pens.append(pen)
        pens = [p if (p != 15 and (mask >> p) & 1) else 15 for p in pens]
        out = bytearray(8)
        for half in (0, 1):
            for x in range(8):
                pen = pens[half * 8 + x]
                for j, byte in enumerate((3, 2, 1, 0)):
                    if (pen >> (3 - j)) & 1:
                        out[half * 4 + byte] |= 1 << (7 - x)
        r = bytes(out)
        _ROWCACHE[key] = r
    return r


# --------------------------------------------------------------------------------------------------------------------
# Cadillacs & Dinosaurs
# --------------------------------------------------------------------------------------------------------------------
# (stage, group) -> (pen mask, first tile code, last tile code, first element of the region); overlay code in dino2c.06 uses the same numbers
DINO_REGIONS = {
    (0, 1): (0x7F7F, 0x5800, 0x6BFF, 0x8000), (1, 1): (0x00FE, 0x5800, 0x5FFF, 0xA000),
    (1, 2): (0x7FFE, 0x5800, 0x5FFF, 0xA800), (1, 3): (0x7F00, 0x5800, 0x5FFF, 0xB000),
    (2, 1): (0x0FFF, 0x5800, 0x59FF, 0xB800), (2, 2): (0x01FF, 0x5800, 0x59FF, 0xBA00),
    (3, 1): (0x01FF, 0x5D00, 0x5E3F, 0xBC00), (3, 2): (0x00FF, 0x5D00, 0x5E3F, 0xBE00),
    (4, 1): (0x00FF, 0x5800, 0x6FFF, 0x18000), (4, 2): (0x00BE, 0x5800, 0x6FFF, 0x19800),
    (4, 3): (0x01FF, 0x5800, 0x6FFF, 0x1B000),
    (5, 1): (0x00FE, 0x5800, 0x6FFF, 0xC000), (5, 2): (0x7F80, 0x5800, 0x6FFF, 0xD800),
    (5, 3): (0x7F87, 0x5800, 0x6FFF, 0x1C800),
    (7, 1): (0x7E01, 0x5A00, 0x69FF, 0xF000), (7, 2): (0x00FF, 0x5A00, 0x69FF, 0x1E000),
    (7, 3): (0x01FF, 0x5A00, 0x69FF, 0x1F000),
}


def dino_tilesets():
    codes = {}
    with open(os.path.join(DATA, "dino_tilecodes.txt")) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                st, g, c = line.split()
                codes.setdefault((int(st, 16), int(g)), []).append(int(c, 16))
    for st in (1,):                      # stage 2: every code seen in any group is baked for all three
        allc = sorted(set(c for (s_, g), cs in codes.items() if s_ == st for c in cs))
        for g in (1, 2, 3):
            codes[(st, g)] = allc
    for st in (4, 5, 7):                 # stages 5, 6, S07: the whole range
        for g in (1, 2, 3):
            _m, lo, hi, _b = DINO_REGIONS[(st, g)]
            codes[(st, g)] = list(range(lo, hi + 1))
    sets = []
    for key, (mask, lo, hi, base) in DINO_REGIONS.items():
        for c in codes.get(key, []):
            assert lo <= c <= hi
            sets.append((mask, c, base + c - lo))
    return sets


def build_dino(f):
    """-> dict of output files (before the delta of data/dino2c.delta is applied to the 68000 and Z80 files)"""
    out = {}
    out["dino2c.03"] = bytes(f["cdu_23a.8f"])
    out["dino2c.04"] = bytes(f["cdu_22a.7f"])
    out["dino2c.05"] = bytes(f["cde_21a.6f"])
    out["dino2c.06"] = bytes(SW)
    out["dino.01"] = bytes(f["cd_q.5k"])
    out["dino.11m"] = samples(f, ["cd-q1.1k", "cd-q2.2k", "cd-q3.3k", "cd-q4.4k"])
    out["phoenix.key"] = b"\xff" * 20
    return out


def bake_dino(f, out, log):
    names = {"1m": "cd-1m.3a", "3m": "cd-3m.5a", "2m": "cd-2m.4a", "4m": "cd-4m.6a",
             "5m": "cd-5m.7a", "7m": "cd-7m.9a", "6m": "cd-6m.8a", "8m": "cd-8m.10a"}
    g1 = cps1_graphics({k: f[v] for k, v in names.items()}, GFX_ORDER)
    dec = bytearray(0x1000000)           # decoded region: 16x16 elements of 128 bytes
    dec[0:0x400000] = g1                 # sprite half: elements 0000-7FFF
    dec[0x800000:0xC00000] = g1          # scroll half: elements 10000-17FFF
    for e0, e1 in ((0x8000, 0x10000), (0x18000, 0x20000)):
        dec[e0 * 128:e1 * 128] = b"\xff" * ((e1 - e0) * 128)     # free: transparent
    sets = dino_tilesets()
    log("    baking %d tiles ..." % len(sets))
    for mask, c, dst in sets:
        for r in range(16):
            s = (0x10000 + c) * 128 + r * 8
            d = dst * 128 + r * 8
            dec[d:d + 8] = baked_row(bytes(dec[s:s + 8]), mask)
    for k, fl in enumerate(region_to_files(dec)):
        out["dino2c.%sm" % ("13", "15", "17", "19")[k]] = bytes(fl)


# --------------------------------------------------------------------------------------------------------------------
# The Punisher
# --------------------------------------------------------------------------------------------------------------------
def build_puni(f):
    out = {}
    img = bytearray(0x180000)
    for name, off in (("psu_26.11e", 0x000000), ("psu_30.11f", 0x000001), ("psu_27.12e", 0x040000), ("psu_31.12f", 0x040001),
                      ("psu_24.9e", 0x080000), ("psu_28.9f", 0x080001), ("psu_25.10e", 0x0c0000), ("psu_29.10f", 0x0c0001)):
        d = f[name]
        img[off:off + 2 * len(d):2] = d
    img[0x100000:] = swap16(f["ps_21.6f"])
    img = swap16(bytes(img))             # the ROM files hold the 68000 words byte-swapped
    out["neopuni.03"] = img[0:SW]
    out["neopuni.04"] = img[SW:2 * SW]
    out["neopuni.05"] = img[2 * SW:3 * SW]
    out["neopuni2.06"] = bytes(SW)
    for n in ("neopuni.07", "neopuni.08", "neopuni.09"):
        out[n] = b"\xff" * SW
    out["neopuni.01"] = bytes(f["ps_q.5k"])
    out["neopuni.11m"] = samples(f, ["ps-q1.1k", "ps-q2.2k", "ps-q3.3k", "ps-q4.4k"])
    out["phoenix.key"] = b"\xff" * 20
    return out


def bake_puni(f, out, log, mask=0x7001):
    names = {"1m": "ps-1m.3a", "3m": "ps-3m.5a", "2m": "ps-2m.4a", "4m": "ps-4m.6a",
             "5m": "ps-5m.7a", "7m": "ps-7m.9a", "6m": "ps-6m.8a", "8m": "ps-8m.10a"}
    g1 = cps1_graphics({k: f[v] for k, v in names.items()}, GFX_ORDER)
    dec = bytearray(0x1000000)
    for off in (0x000000, 0x400000, 0x800000, 0xc00000):         # the neocps layout: four copies of the CPS1 graphics
        dec[off:off + 0x400000] = g1
    files = region_to_files(dec)
    raw = files_to_raw(files)
    log("    baking 32768 tiles ...")
    for e in range(0x8000):              # element 8000+e = tile e with only the masked pens (as the neocps layout's mirror)
        for r in range(16):
            s = ((0x10000 + e) * 16 + r) * 8
            d = ((0x8000 + e) * 16 + r) * 8
            raw[d:d + 8] = baked_row(bytes(raw[s:s + 8]), mask)
    for k, fl in enumerate(raw_to_files(raw)):
        out["neopuni2.%sm" % ("13", "15", "17", "19")[k]] = bytes(fl)


# --------------------------------------------------------------------------------------------------------------------
# the delta: what differs from the plain conversion (68000 changes, the Z80 code, the code in the extra program file)
# --------------------------------------------------------------------------------------------------------------------
def read_delta(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:4] != b"C2FX":
        raise SystemExit("%s is not a cps2fix data file" % path)
    d = zlib.decompress(raw[4:])
    pos = 0
    (n,) = struct.unpack_from("<I", d, pos)
    pos += 4
    files = {}
    for _ in range(n):
        ln = d[pos]
        name = d[pos + 1:pos + 1 + ln].decode()
        pos += 1 + ln
        (nops,) = struct.unpack_from("<I", d, pos)
        pos += 4
        ops = []
        for _ in range(nops):
            off, length = struct.unpack_from("<II", d, pos)
            pos += 8
            ops.append((off, d[pos:pos + length]))
            pos += length
        files[name] = ops
    return files


def write_delta(path, files):
    d = struct.pack("<I", len(files))
    for name, ops in files.items():
        nb = name.encode()
        d += bytes([len(nb)]) + nb + struct.pack("<I", len(ops))
        for off, data in ops:
            d += struct.pack("<II", off, len(data)) + data
    with open(path, "wb") as fh:
        fh.write(b"C2FX" + zlib.compress(d, 9))


def make_ops(base, target, gap=16):
    """runs of bytes of target that differ from base (runs closer than gap bytes are merged)"""
    assert len(base) == len(target)
    ops, i, n = [], 0, len(base)
    while i < n:
        if base[i] == target[i]:
            i += 1
            continue
        j = i
        last = i
        while j < n and j - last <= gap:
            if base[j] != target[j]:
                last = j
            j += 1
        ops.append((i, bytes(target[i:last + 1])))
        i = last + 1
    return ops


def apply_ops(buf, ops):
    b = bytearray(buf)
    for off, data in ops:
        b[off:off + len(data)] = data
    return bytes(b)


# --------------------------------------------------------------------------------------------------------------------
# the output sets
# --------------------------------------------------------------------------------------------------------------------
GAMES = {
    "dino": dict(
        title="Cadillacs and Dinosaurs (USA) -> CPS2", files=DINO_FILES, mame="dino2c",
        delta="dino2c.delta", build=build_dino, bake=bake_dino,
        zip_order=["dino.01", "dino.11m", "dino2c.03", "dino2c.04", "dino2c.05", "dino2c.06", "dino2c.13m", "dino2c.15m",
                   "dino2c.17m", "dino2c.19m", "phoenix.key"],
        prog=["dino2c.03", "dino2c.04", "dino2c.05", "dino2c.06"], z80="dino.01", samples="dino.11m",
        gfx=["dino2c.13m", "dino2c.15m", "dino2c.17m", "dino2c.19m"], ds_name="Dino CPS2 Port"),
    "punisher": dict(
        title="The Punisher (USA) -> CPS2", files=PUNI_FILES, mame="neopuni2",
        delta="neopuni2.delta", build=build_puni, bake=bake_puni,
        zip_order=["neopuni.01", "neopuni.03", "neopuni.04", "neopuni.05", "neopuni2.06", "neopuni.07", "neopuni.08",
                   "neopuni.09", "neopuni.11m", "neopuni2.13m", "neopuni2.15m", "neopuni2.17m", "neopuni2.19m", "phoenix.key"],
        prog=["neopuni.03", "neopuni.04", "neopuni.05", "neopuni2.06", "neopuni.07", "neopuni.08", "neopuni.09"],
        z80="neopuni.01", samples="neopuni.11m",
        gfx=["neopuni2.13m", "neopuni2.15m", "neopuni2.17m", "neopuni2.19m"], ds_name="PunisherNeoCPS"),
}


def build_game(key, index, log):
    g = GAMES[key]
    f = load(index, g["files"])
    out = g["build"](f)
    delta = read_delta(os.path.join(DATA, g["delta"]))
    for name, ops in delta.items():
        out[name] = apply_ops(out[name], ops)
    g["bake"](f, out, log)
    manifest = json.load(open(os.path.join(DATA, "manifest.json")))[g["mame"]]
    bad = False
    for name, (size, crc, sha1) in manifest.items():
        d = out[name]
        if len(d) != size or crc32(d) != int(crc, 16) or hashlib.sha1(d).hexdigest() != sha1:
            print("    SELF-CHECK FAILED for %s (crc %08x, expected %s)" % (name, crc32(d), crc))
            bad = True
    if bad:
        raise SystemExit("The files built do not match the release; the input files are probably another dump. Nothing written.")
    return out


def write_zip(path, names, out):
    try:
        z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6)
    except TypeError:                    # Python 3.6
        z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    with z:
        for n in names:
            zi = zipfile.ZipInfo(n, (1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, out[n])


def write_darksoft(folder, g, out):
    """Darksoft multi-board flash layout: flash.01 = Z80 image x32, flash.02 = the 68000 files and FF, flash.03 = samples,
    flash.05/.07/.09/.11 = graphics, key = phoenix key, NAME = 14 characters + '=W'"""
    prog = b"".join(out[n] for n in g["prog"])
    assert len(prog) <= 0x400000
    files = {
        "NAME": (g["ds_name"] + "=W").encode(),
        "flash.01": out[g["z80"]] * 32,
        "flash.02": prog + b"\xff" * (0x400000 - len(prog)),
        "flash.03": out[g["samples"]],
        "flash.05": out[g["gfx"][0]], "flash.07": out[g["gfx"][1]], "flash.09": out[g["gfx"][2]], "flash.11": out[g["gfx"][3]],
        "key": out["phoenix.key"],
    }
    os.makedirs(folder, exist_ok=True)
    for n, d in files.items():
        with open(os.path.join(folder, n), "wb") as fh:
            fh.write(d)


def main():
    ap = argparse.ArgumentParser(description="Builds fixed CPS2 sets of Cadillacs & Dinosaurs and The Punisher from the original CPS1 zips.")
    ap.add_argument("--roms", default=os.path.join(HERE, "roms"), help="folder with the original zips (default: roms next to this script)")
    ap.add_argument("--out", default=os.path.join(HERE, "output"), help="output folder (default: output next to this script)")
    ap.add_argument("--game", default="all", choices=["all", "dino", "punisher"])
    ap.add_argument("--no-mame", action="store_true", help="do not write the MAME zips")
    ap.add_argument("--no-darksoft", action="store_true", help="do not write the Darksoft folders")
    ap.add_argument("--check", action="store_true", help="only check the input files")
    a = ap.parse_args()
    t0 = time.time()
    print("cps2fix - Cadillacs & Dinosaurs / The Punisher CPS2 sets")
    if not os.path.isdir(a.roms):
        raise SystemExit("ROM folder %s does not exist" % a.roms)
    print("ROM folder: %s" % a.roms)
    index = RomIndex(a.roms)
    print("zip files found: %s" % (", ".join(index.zips) or "none"))
    # which regional sets are present (informational)
    for name, desc, crcs in OTHER_SETS:
        if any(index.has(c, 0x80000) or index.has(c, 0x20000) for c in crcs[:2]):
            if name in ("dinou", "punisheru"):
                used = "used (68000 code)"
            elif name in ("dino", "punisher"):
                used = "used as the parent set (graphics, sound and shared program ROM; its own 68000 code is another revision)"
            else:
                used = "recognised, not used (its 68000 code is another revision, see README.md)"
            print("  set %-10s %s: %s" % (name, desc, used))
    results = {}
    for key in (["dino", "punisher"] if a.game == "all" else [a.game]):
        g = GAMES[key]
        print("\n== %s ==" % g["title"])
        print("  checking the original files:")
        if not check_inputs(index, g["files"]):
            print("  -> cannot build this game: put the missing files (zips as in MAME 0.2xx) into %s" % a.roms)
            results[key] = False
            continue
        if a.check:
            results[key] = True
            continue
        print("  building ...")
        out = build_game(key, index, lambda s: print(s))
        if not a.no_mame:
            os.makedirs(os.path.join(a.out, "mame"), exist_ok=True)
            p = os.path.join(a.out, "mame", g["mame"] + ".zip")
            write_zip(p, g["zip_order"], out)
            print("  wrote %s" % p)
        if not a.no_darksoft:
            p = os.path.join(a.out, "darksoft", g["mame"])
            write_darksoft(p, g, out)
            print("  wrote %s" % p)
        results[key] = True
    print("\ndone in %.0f s: %s" % (time.time() - t0, ", ".join("%s %s" % (k, "ok" if v else "NOT BUILT") for k, v in results.items())))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
