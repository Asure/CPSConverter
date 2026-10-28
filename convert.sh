#!/bin/sh
# cps2fix - one command: builds the fixed CPS2 sets of Cadillacs & Dinosaurs and The Punisher from the original zips in roms/
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
    echo "Python 3 was not found. Install it with your package manager (for example: sudo apt install python3) and run this again."
    exit 1
fi
"$PY" cps2fix.py "$@"
