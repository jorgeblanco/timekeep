#!/bin/bash

PREFIX=/usr/local

INSTALLDIR="$PREFIX/share/timekeep"
BINDIR="$PREFIX/bin"

# Are we root?
if [[ $EUID -ne 0 ]]; then
    echo "You must be root to run this script." 2>&1
    exit 1
else
    mkdir -p "$INSTALLDIR"
    cp *.{png,svg,py} "$INSTALLDIR/"
    ln -s "$INSTALLDIR/timekeep.py" "$BINDIR/timekeep"
fi
