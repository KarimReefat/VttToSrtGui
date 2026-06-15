pyinstaller -w -y --clean -i ./icon.png --add-data="./icon.png;." --exclude-module tcl --exclude-module tkinter --exclude-module Tkinter --exclude-module Tkconstants --exclude-module tk --exclude-module unittest --exclude-module email --exclude-module http --exclude-module xml --exclude-module pydoc --exclude-module distutils --exclude-module setuptools --exclude-module gtkagg --exclude-module tkagg --exclude-module bsddb --exclude-module curses --exclude-module email --exclude-module pywin.debugger --exclude-module pywin.debugger.dbgcon --exclude-module pywin.dialogs gui3.py


