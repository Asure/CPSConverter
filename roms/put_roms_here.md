# Put the original ROM zips here

Copy the original MAME zips of these sets into this folder (the file names are the MAME names; the zips can stay as they are):

| Game | Needed zips | Why |
|---|---|---|
| Cadillacs and Dinosaurs | `dinou.zip` (USA, 930201) and `dino.zip` (World, 930201, the parent set) | `dinou.zip` holds only the two program ROMs that differ, everything else is in `dino.zip` |
| The Punisher | `punisheru.zip` (USA, 930422) and `punisher.zip` (World, 930422, the parent set) | `punisheru.zip` holds only the program ROMs, everything else is in `punisher.zip` |

`dinoa.zip` (Asia) and `punisherj.zip` (Japan) may be here too, they are recognised and ignored. Then run `convert.bat` (Windows) or
`./convert.sh` (Linux) one folder up. The tool checks every file by CRC32 before it builds anything; `README.md` lists them all.

This folder is git-ignored apart from this file.
