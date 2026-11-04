#!/usr/bin/env python3
"""Maintainer tool: builds release/data/*.delta and manifest.json from the finished sets of the repository.

usage: python3 tools/make_data.py [roms folder with the original zips]

The delta of a game is what its finished set differs by from the plain conversion cps2fix.py makes from the original files:
the 68000 changes (the CPS2 port and the fixes), the changed Z80 code and the code in the extra program file. The graphics are baked by
cps2fix.py itself and only checked here. The finished sets are dino/romsets/dino2c.zip and punisher/romsets/neopuni2.zip."""
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REL = os.path.dirname(HERE)
REPO = os.path.dirname(REL)
sys.path.insert(0, REL)
import cps2fix as c  # noqa: E402

roms = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REL, "roms")
index = c.RomIndex(roms)
FINISHED = {"dino": os.path.join(REPO, "dino", "romsets", "dino2c.zip"), "punisher": os.path.join(REPO, "punisher", "romsets", "neopuni2.zip"),
            "wofch": os.path.join(REPO, "wofch", "work", "romsets", "wof2.zip")}
DELTA_FILES = {"dino": ["dino2c.03", "dino2c.04", "dino2c.05", "dino2c.06", "dino.01"],
               "punisher": ["neopuni.03", "neopuni.04", "neopuni.05", "neopuni2.06", "neopuni.01"],
               "wofch": ["wof2.03", "wof2.04", "wof2.shim", "wof2.01"]}
manifest = {}


def make_wof_map(f):
    """data/wof2_map.json: the baked regions of the overlay (wofch/scenes.json), the scroll 3 block range and the address ranges of the Z80 code that are fetched
    as opcodes (taken from the finished wof2.01; ranges only, no code bytes)"""
    z = zipfile.ZipFile(FINISHED["wofch"]).read("wof2.01")
    op, da = c.kabuki_views(f["tk2_qa.5k"])
    ranges, cur = [], None
    for a in range(0x8000):
        if z[a] == op[a] and op[a] != da[a]:
            if cur is None:
                cur = [a, a + 1]
            else:
                cur[1] = a + 1
        elif z[a] != da[a] and z[a] != op[a]:
            pass                        # patched byte: part of the delta
        elif op[a] != da[a] and cur is not None:
            ranges.append(cur)
            cur = None
        # op == da: either view is right, the open range simply continues
    if cur:
        ranges.append(cur)
    sc = json.load(open(os.path.join(REPO, "wofch", "scenes.json")))
    m = {"regions": sc["regions"], "scroll3": [0xBC00, 0x1C00, 0x400], "z80_op": ranges}
    json.dump(m, open(os.path.join(REL, "data", "wof2_map.json"), "w"), separators=(",", ":"))
    print("wof2_map.json: %d regions, %d Z80 opcode ranges" % (len(m["regions"]), len(ranges)))


for key, g in c.GAMES.items():
    if not c.check_inputs(index, g["files"]):
        raise SystemExit("original files for %s missing" % key)
    f = c.load(index, g["files"])
    if key == "wofch":
        make_wof_map(f)
    out = g["build"](f)
    target = zipfile.ZipFile(FINISHED[key])
    delta = {}
    for n in DELTA_FILES[key]:
        ops = c.make_ops(out[n], target.read(n))
        delta[n] = ops
        print("%-14s %d runs, %d bytes" % (n, len(ops), sum(len(d) for _o, d in ops)))
        out[n] = c.apply_ops(out[n], ops)
    g["bake"](f, out, print)
    mf = {}
    for n in g["zip_order"]:
        t = target.read(n)
        if out[n] != t:
            raise SystemExit("%s differs from the finished set after the delta" % n)
        mf[n] = (len(t), "%08x" % c.crc32(t), c.hashlib.sha1(t).hexdigest())
    manifest[g["mame"]] = mf
    c.write_delta(os.path.join(REL, "data", g["delta"]), delta)
json.dump(manifest, open(os.path.join(REL, "data", "manifest.json"), "w"), indent=1)
print("wrote data files")
