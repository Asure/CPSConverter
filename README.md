# cps2fix - Cadillacs & Dinosaurs and The Punisher for CPS2, built from your own ROMs

One click turns the original CPS1 ROM zips of **Cadillacs and Dinosaurs** and **The Punisher** into the fixed CPS2 versions that run on a real CPS2
board (a Darksoft multi-board, tested) and in MAME. You supply the original zips; nothing in this folder contains a ROM of the games, only the
changes (see "What is in the data files" below).

* Windows: double-click **`convert.bat`**. If Python 3 is not installed it asks before downloading the small official Python from python.org into the `runtime` folder (checksum-verified, nothing is installed).
* Linux / macOS: run **`./convert.sh`** (needs `python3`).

It takes about 20 seconds and writes everything into the `output` folder:

```
output/
  mame/dino2c.zip            MAME set  (needs the MAME driver patch, see "MAME")
  mame/neopuni2.zip          MAME set
  darksoft/dino2c/           Darksoft multi-board files (copy the folder content to the card)
  darksoft/neopuni2/
```

## What you need

Put the original MAME zips into the `roms` folder (next to `convert.bat`). The tool finds the files by their **CRC32** (not by zip name), checks
each one **before it builds anything** and tells you exactly which file is missing or has the wrong CRC. The zips are the ones MAME uses, a
clone zip (`dinou`, `punisheru`) holds only the files that differ from its parent (`dino`, `punisher`), so you need both.

| Game | Zips | MAME name / region |
|---|---|---|
| Cadillacs and Dinosaurs | `dinou.zip` + `dino.zip` | `dinou` USA 930201 (68000 code) + `dino` World 930201 (graphics, sound, one program ROM) |
| The Punisher | `punisheru.zip` + `punisher.zip` | `punisheru` USA 930422 (68000 code) + `punisher` World 930422 (graphics, sound, one program ROM) |

`dinoa.zip` (Asia) and `punisherj.zip` (Japan) may sit in the folder too. They are recognised and ignored, see "Regions".

### Cadillacs and Dinosaurs - files checked

| File (inside the zip) | Size | CRC32 | Zip |
|---|---:|---|---|
| `cdu_23a.8f` | 524288 | `7c2543cd` | `dinou.zip` |
| `cdu_22a.7f` | 524288 | `d19f981e` | `dinou.zip` |
| `cde_21a.6f` | 524288 | `66d23de2` | `dino.zip` |
| `cd-1m.3a` | 524288 | `8da4f917` | `dino.zip` |
| `cd-3m.5a` | 524288 | `6c40f603` | `dino.zip` |
| `cd-2m.4a` | 524288 | `09c8fc2d` | `dino.zip` |
| `cd-4m.6a` | 524288 | `637ff38f` | `dino.zip` |
| `cd-5m.7a` | 524288 | `470befee` | `dino.zip` |
| `cd-7m.9a` | 524288 | `22bfb7a3` | `dino.zip` |
| `cd-6m.8a` | 524288 | `e7599ac4` | `dino.zip` |
| `cd-8m.10a` | 524288 | `211b4b15` | `dino.zip` |
| `cd_q.5k` | 131072 | `605fdb0b` | `dino.zip` |
| `cd-q1.1k` | 524288 | `60927775` | `dino.zip` |
| `cd-q2.2k` | 524288 | `770f4c47` | `dino.zip` |
| `cd-q3.3k` | 524288 | `2f273ffc` | `dino.zip` |
| `cd-q4.4k` | 524288 | `2c67821d` | `dino.zip` |

### The Punisher - files checked

| File (inside the zip) | Size | CRC32 | Zip |
|---|---:|---|---|
| `psu_26.11e` | 131072 | `9236d121` | `punisheru.zip` |
| `psu_30.11f` | 131072 | `8320e501` | `punisheru.zip` |
| `psu_27.12e` | 131072 | `61c960a1` | `punisheru.zip` |
| `psu_31.12f` | 131072 | `78d4c298` | `punisheru.zip` |
| `psu_24.9e` | 131072 | `1cfecad7` | `punisheru.zip` |
| `psu_28.9f` | 131072 | `bdf921c1` | `punisheru.zip` |
| `psu_25.10e` | 131072 | `c51acc94` | `punisheru.zip` |
| `psu_29.10f` | 131072 | `52dce1ca` | `punisheru.zip` |
| `ps_21.6f` | 524288 | `8affa5a9` | `punisher.zip` |
| `ps-1m.3a` | 524288 | `77b7ccab` | `punisher.zip` |
| `ps-3m.5a` | 524288 | `0122720b` | `punisher.zip` |
| `ps-2m.4a` | 524288 | `64fa58d4` | `punisher.zip` |
| `ps-4m.6a` | 524288 | `60da42c8` | `punisher.zip` |
| `ps-5m.7a` | 524288 | `c54ea839` | `punisher.zip` |
| `ps-7m.9a` | 524288 | `04c5acbd` | `punisher.zip` |
| `ps-6m.8a` | 524288 | `a544f4cc` | `punisher.zip` |
| `ps-8m.10a` | 524288 | `8f02f436` | `punisher.zip` |
| `ps_q.5k` | 131072 | `49ff4446` | `punisher.zip` |
| `ps-q1.1k` | 524288 | `31fd8726` | `punisher.zip` |
| `ps-q2.2k` | 524288 | `980a9eef` | `punisher.zip` |
| `ps-q3.3k` | 524288 | `0dd44491` | `punisher.zip` |
| `ps-q4.4k` | 524288 | `bed42f03` | `punisher.zip` |

The files not listed (PAL/GAL dumps `*.1a`, `ioa1`, ... in the parent zips) are not used.

## Regions: why USA only

The CPS2 conversions this tool builds are ports of the **USA** program code (`dinou`, `punisheru`). The World, Asia and Japan sets are other revisions of the
program: their 68000 code differs from the USA code in 70,000 to 200,000 bytes (measured), so the port's patch sites and our fixes (every address
in them belongs to the USA code) do not apply. The World zips are still needed because the USA zips are clones: the graphics, the sound samples,
the Z80 program and one of the program ROMs are shared. A World, Asia or Japan version would need its own port; the region of the
conversions is the USA one (the game's region/coin settings are in its service menu as usual).

## What the tool does

1. Looks through every zip in `roms` (and loose `.bin` style files of 128/512 KB) and indexes the files by CRC32.
2. Checks that all files of a game are there and correct (the tables above). Nothing is written if one is wrong.
3. Builds the CPS2 files: the 68000 program from the USA files plus the port and the fixes (`data/*.delta`), the Z80 program, the QSound samples
   (CPS2 layout), the sprite/scroll graphics in the CPS2 layout and the pen-mask overlay tiles (baked from the original graphics, the tile lists are in
   `data/dino_tilecodes.txt` and in `cps2fix.py`).
4. Checks every file it built against the CRC32 **and SHA1** of the tested release (`data/manifest.json`). If anything differs nothing is written
   (that means the inputs were another dump).
5. Writes the MAME zips and the Darksoft folders.

The result is deterministic: the same inputs always give the same bytes. The files built are the ones that were tested on a real board.

### Files built

**dino2c** (`output/mame/dino2c.zip`):

| File | Size | CRC32 |
|---|---:|---|
| `dino.01` | 131072 | `1ac4eda1` |
| `dino.11m` | 4194304 | `a65584f4` |
| `dino2c.03` | 524288 | `e995da40` |
| `dino2c.04` | 524288 | `61f1f75d` |
| `dino2c.05` | 524288 | `66d23de2` |
| `dino2c.06` | 524288 | `8e124d66` |
| `dino2c.13m` | 4194304 | `d531fd31` |
| `dino2c.15m` | 4194304 | `4db5f4ff` |
| `dino2c.17m` | 4194304 | `cf7af7a1` |
| `dino2c.19m` | 4194304 | `09b6fa3f` |
| `phoenix.key` | 20 | `2cf772b0` |

**neopuni2** (`output/mame/neopuni2.zip`):

| File | Size | CRC32 |
|---|---:|---|
| `neopuni.01` | 131072 | `749d5466` |
| `neopuni.03` | 524288 | `f68a92ae` |
| `neopuni.04` | 524288 | `64a5ff42` |
| `neopuni.05` | 524288 | `8affa5a9` |
| `neopuni2.06` | 524288 | `85358c1a` |
| `neopuni.07` | 524288 | `504bf849` |
| `neopuni.08` | 524288 | `504bf849` |
| `neopuni.09` | 524288 | `504bf849` |
| `neopuni.11m` | 4194304 | `5ed2c629` |
| `neopuni2.13m` | 4194304 | `f02631f5` |
| `neopuni2.15m` | 4194304 | `b8d541d2` |
| `neopuni2.17m` | 4194304 | `1f26a7b6` |
| `neopuni2.19m` | 4194304 | `ca722725` |
| `phoenix.key` | 20 | `2cf772b0` |

(`dino2c.05` and `neopuni.05` are the original `cde_21a.6f` / `ps_21.6f`, `neopuni.07-.09` are filled with `FF`.)

## What is fixed

**Cadillacs and Dinosaurs** (`dino2c`): the CPS2 port's coin lockout (coins are accepted), the work-RAM self-test it overwrote, three ROM-check routines that
failed in the port (the penalties the callers apply no longer happen), and the **pen-mask overlay**: CPS2 has no per-pen priority, so the tiles that
cover the sprites on CPS1 (doorway, forest and swamp plants and trunks, desert rocks and cacti, garage fences, stages 5 and 6 and the last stage) are
drawn again over the sprites from baked copies; the overlay is off outside play (continue screen, intros). Details: `dino/dino_tools.md` in the repository.

**The Punisher** (`neopuni2`): the 15 tamper checks of the CPS2 conversion (they failed because the port changed the bytes they read), the bus fight
tire priority, the stage 3 start crates, the stage 5 trash strip and forest, the stage 6 pillars, pipe room and elevator, the bus ledge, the
continue screen sprite priority, the coin lockout and the lifebar. Details: `punisher/punisher_fixes.md` in the repository.

## MAME

The two sets need two driver entries, `dino2c` and `neopuni2`, in a MAME that has the CPS2 driver. `mame/cps2fix_drivers.patch` adds them (to
`src/mame/capcom/cps2.cpp` and `src/mame/mame.lst`, with the real CRCs). In the MAME source folder:

```
patch -p1 < cps2fix_drivers.patch
make SOURCES=src/mame/capcom/cps1.cpp,src/mame/capcom/cps2.cpp SUBTARGET=cps2fix NOWERROR=1 TOOLS=0 -j8
./cps2fix dino2c -rompath "<folder with the zips>"
```

(A full MAME also works, `SOURCES=` only makes the build much smaller.) The sound needs MAME's own `qsound_hle.zip` (it holds the DSP firmware
`dl-1425.bin`) in the same rompath; it is not part of the sets and not built here. Credits in MAME: key 5 / 6 coins, 1 / 2 start.

## Darksoft multi-board

Copy the **content** of `output/darksoft/dino2c` (or `neopuni2`) to a folder on the card as for any Darksoft game. The files are `NAME`, `key`
and `flash.01 .02 .03 .05 .07 .09 .11` (4 MB each): `flash.01` Z80 program (32 copies), `flash.02` the 68000 program files one after another (padded
with `FF`), `flash.03` the QSound samples, `flash.05/.07/.09/.11` the graphics, `key` the null phoenix key (the program is not encrypted), `NAME` the title
(`Dino CPS2 Port`, `PunisherNeoCPS`, 14 characters + `=W`).

## Troubleshooting

| Message | Meaning |
|---|---|
| `MISSING <file> ... (from dino.zip)` | the file is not in any zip in `roms`; get the zip that MAME 0.2xx uses for that set |
| `WRONG <file> expected ..., <zip> has ...` | a zip has a file of that name with another CRC (another dump or a damaged file) |
| `SELF-CHECK FAILED` | the inputs passed the CRC check but the result is not the tested one; please report it, nothing is written |
| `Python 3 was not found` | install Python 3 from python.org (Windows: `convert.bat` offers to download the official embeddable Python into `runtime`; `convert.bat --get-python` does that on request) |

`python3 cps2fix.py --check` only checks the files; `--game dino` / `--game punisher`, `--no-mame`, `--no-darksoft`, `--roms DIR`, `--out DIR` select
what is done.

## What is in the data files (and what is not)

`data/dino2c.delta` and `data/neopuni2.delta` hold only the *differences* to the plain conversion of the original files: a few hundred bytes of
68000 patches in the program ROMs (the CPS2 port's I/O changes and our fixes), the code added at `180000` (the port's startup code and our overlay
routines, about 15 KB), and the first 32 KB of the Z80 program (the changed sound driver). `data/manifest.json` has the CRC32/SHA1 of every file built.
The graphics, the samples and the rest of the program come from **your** zips. The program changes build on the third-party CPS2 conversions of
the two games (the Dino CPS2 port and neocps1's Punisher set); the Z80 changes derive from Capcom's sound program, so think about that before you
redistribute the data files.

## Folder

| Path | |
|---|---|
| `convert.bat`, `convert.sh` | one-click launchers |
| `cps2fix.py` | the tool (Python 3.7+, standard library only; 3.6 works too) |
| `data/` | deltas, tile code list, manifest |
| `mame/cps2fix_drivers.patch` | MAME driver entries |
| `runtime/` | created only if you let `convert.bat` download the official embeddable Python (git-ignored) |
| `roms/` | your original zips (git-ignored) |
| `output/` | what is built (git-ignored) |
| `tools/make_data.py` | maintainer: rebuilds `data/` from the finished sets `dino/romsets/dino2c.zip` and `punisher/romsets/neopuni2.zip` of the repository; `tools/make_mame_patch.py` rebuilds the MAME patch |

`tools/make_data.py` expects the finished sets in the author's research repository (`dino/romsets/dino2c.zip`, `punisher/romsets/neopuni2.zip`), so it only works there. When those sets change (new overlay scenes, fixes), rebuild the sets as before, then run `python3 tools/make_data.py` and
`python3 tools/make_mame_patch.py <clean cps2.cpp> <clean mame.lst>`; `python3 cps2fix.py` must then report all files ok.

## License

cps2fix (the tool, the launchers, the maintainer scripts and the driver patch) is free software under the **GNU General Public License v3.0**, see `LICENSE`.
The licence covers this tool only. It gives no rights to the games' ROMs, to Capcom's code, or to the third-party CPS2 conversions the data files build on.
