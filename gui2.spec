# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui2.py'],
             pathex=['D:\\New\\Projects\\subtest\\Repos\\VttToSrtGui'],
             binaries=[],
             datas=[('./icon.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tcl', 'tkinter', 'Tkinter', 'Tkconstants', 'tk', 'unittest', 'email', 'http', 'xml', 'pydoc', 'distutils', 'setuptools', 'gtkagg', 'tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='gui2',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='gui2')
