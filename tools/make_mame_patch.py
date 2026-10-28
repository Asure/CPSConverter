#!/usr/bin/env python3
"""Maintainer tool: writes mame/cps2fix_drivers.patch (adds the sets dino2c and neopuni2, with the real CRCs and SHA1s of the files cps2fix.py
builds, to src/mame/capcom/cps2.cpp and src/mame/mame.lst of a MAME source tree).
usage: python3 tools/make_mame_patch.py <cps2.cpp of a clean MAME tree> <mame.lst of the same tree>"""
import difflib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REL = os.path.dirname(HERE)
mf = json.load(open(os.path.join(REL, "data", "manifest.json")))


def h(name, ms):
    size, crc, sha1 = ms[name]
    return "CRC(%s) SHA1(%s)" % (crc, sha1)


def dino_block():
    m = mf["dino2c"]
    L = ["ROM_START( dino2c )",
         '\tROM_REGION( CODE_SIZE, "maincpu", 0 ) // 68000 code (decrypted, CPS1 Cadillacs and Dinosaurs port with fixes and overlay)']
    for n, off in (("dino2c.03", 0), ("dino2c.04", 0x80000), ("dino2c.05", 0x100000), ("dino2c.06", 0x180000)):
        L.append('\tROM_LOAD16_WORD_SWAP( "%s", 0x%06x, 0x80000, %s )' % (n, off, h(n, m)))
    L += ["", '\tROM_REGION16_BE( CODE_SIZE, "user1", 0 )', "\tROM_FILL( 0x000000, 0x100000, 0x00 )", "",
          '\tROM_REGION( 0x1000000, "gfx", 0 )']
    for i, n in enumerate(("dino2c.13m", "dino2c.15m", "dino2c.17m", "dino2c.19m")):
        L.append('\tROM_LOAD64_WORD( "%s", 0x%07x, 0x400000, %s )' % (n, i * 2, h(n, m)))
    L += ["", '\tROM_REGION( QSOUND_SIZE, "audiocpu", 0 ) // 64k for the audio CPU (+banks)',
          '\tROM_LOAD( "dino.01", 0x00000, 0x08000, %s )' % h("dino.01", m), "\tROM_CONTINUE(         0x10000, 0x18000 )", "",
          '\tROM_REGION( 0x400000, "qsound", 0 ) // QSound samples',
          '\tROM_LOAD16_WORD_SWAP( "dino.11m", 0x000000, 0x400000, %s )' % h("dino.11m", m), "",
          '\tROM_REGION( 0x20, "key", 0 )', '\tROM_LOAD( "phoenix.key", 0x000000, 0x000014, %s )' % h("phoenix.key", m), "ROM_END", ""]
    return L


def puni_block():
    m = mf["neopuni2"]
    L = ["ROM_START( neopuni2 )", '\tROM_REGION( CODE_SIZE, "maincpu", 0 ) // 68000 code (decrypted, CPS1 Punisher port with fixes and overlay)']
    for i, n in enumerate(("neopuni.03", "neopuni.04", "neopuni.05", "neopuni2.06", "neopuni.07", "neopuni.08", "neopuni.09")):
        L.append('\tROM_LOAD16_WORD_SWAP( "%s", 0x%06x, 0x80000, %s )' % (n, i * 0x80000, h(n, m)))
    L += ["", '\tROM_REGION( 0x1000000, "gfx", 0 )']
    for i, n in enumerate(("neopuni2.13m", "neopuni2.15m", "neopuni2.17m", "neopuni2.19m")):
        L.append('\tROM_LOAD64_WORD( "%s", 0x%07x, 0x400000, %s )' % (n, i * 2, h(n, m)))
    L += ["", '\tROM_REGION( QSOUND_SIZE, "audiocpu", 0 ) // 64k for the audio CPU (+banks)',
          '\tROM_LOAD( "neopuni.01", 0x00000, 0x08000, %s )' % h("neopuni.01", m), "\tROM_CONTINUE(         0x10000, 0x18000 )", "",
          '\tROM_REGION( 0x400000, "qsound", 0 ) // QSound samples',
          '\tROM_LOAD16_WORD_SWAP( "neopuni.11m", 0x000000, 0x400000, %s )' % h("neopuni.11m", m), "",
          '\tROM_REGION( 0x20, "key", 0 )', '\tROM_LOAD( "phoenix.key", 0x000000, 0x000014, %s )' % h("phoenix.key", m), "ROM_END", ""]
    return L


GAMES = [
    'GAME( 1993, dino2c,      0,           dead_cps2, cps2_3p3b,     cps2_state, init_cps2, ROT0, "bootleg", "Cadillacs and Dinosaurs (CPS2 port, USA, fixed, with overlay)", MACHINE_SUPPORTS_SAVE )',
    'GAME( 1993, neopuni2,    0,           dead_cps2, cps2_2p2b,     cps2_state, init_cps2, ROT0, "bootleg", "The Punisher (CPS2 port, USA, fixed, with overlay)", MACHINE_SUPPORTS_SAVE )',
]
cpp = open(sys.argv[1]).read().splitlines()
lst = open(sys.argv[2]).read().splitlines()
new = list(cpp)
i = new.index("} // anonymous namespace")
new[i:i] = dino_block() + puni_block()
while new and new[-1] == "":
    new.pop()
new += GAMES
out = list(difflib.unified_diff(cpp, new, "a/src/mame/capcom/cps2.cpp", "b/src/mame/capcom/cps2.cpp", lineterm="", n=3))
j = lst.index("@source:capcom/cps2.cpp")
k = j + 1
while k < len(lst) and lst[k].strip():
    k += 1
nl = list(lst)
nl[k:k] = ["dino2c", "neopuni2"]
out += list(difflib.unified_diff(lst, nl, "a/src/mame/mame.lst", "b/src/mame/mame.lst", lineterm="", n=3))
open(os.path.join(REL, "mame", "cps2fix_drivers.patch"), "w").write("\n".join(out) + "\n")
print("wrote mame/cps2fix_drivers.patch")
