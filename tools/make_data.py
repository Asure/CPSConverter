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
FINISHED = {"dino": os.path.join(REPO, "dino", "romsets", "dino2c.zip"), "punisher": os.path.join(REPO, "punisher", "romsets", "neopuni2.zip")}
DELTA_FILES = {"dino": ["dino2c.03", "dino2c.04", "dino2c.05", "dino2c.06", "dino.01"],
               "punisher": ["neopuni.03", "neopuni.04", "neopuni.05", "neopuni2.06", "neopuni.01"]}
manifest = {}
for key, g in c.GAMES.items():
    if not c.check_inputs(index, g["files"]):
        raise SystemExit("original files for %s missing" % key)
    f = c.load(index, g["files"])
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
