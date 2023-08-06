# -*- mode: python -*-
# -*- encoding: utf-8 -*-

# This file needs to be invoked with "pyinstaller resources/pivman.spec" from
# the parent directory!

import os
import sys
import re
from glob import glob
from getpass import getpass

NAME = "YubiKey PIV Manager"

WIN = sys.platform in ['win32', 'cygwin']
OSX = sys.platform in ['darwin']

ICON = os.path.join('resources', 'pivman-large.png')
if WIN:
    ICON = os.path.join('resources', 'pivman.ico')

elif OSX:
    ICON = os.path.join('resources', 'pivman.icns')

a = Analysis(['scripts/pivman'],
             pathex=[''],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

# DLLs, dylibs and executables should go here.
libs = glob('lib/*')
for filename in libs:
    a.datas.append((filename[4:], filename, 'BINARY'))

# Read version string
with open('pivman/__init__.py', 'r') as f:
    match = re.search(r"(?m)^__version__\s*=\s*['\"](.+)['\"]$", f.read())
    ver_str = match.group(1)

# Read version information on Windows.
VERSION = None
if WIN:
    VERSION = 'build/file_version_info.txt'

    ver_tup = tuple(map(int, ver_str.split('.')))
    while len(ver_tup) < 4:
        ver_tup += (0,)
    assert len(ver_tup) == 4

    # Write version info.
    with open(VERSION, 'w') as f:
        f.write("""
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four
    # items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=%(ver_tup)r,
    prodvers=%(ver_tup)r,
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x0,
    # Contains a bitmask that specifies the Boolean attributes
    # of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904E4',
        [StringStruct(u'FileDescription', u'YubiKey PIV Manager'),
        StringStruct(u'FileVersion', u'%(ver_str)s'),
        StringStruct(u'InternalName', u'pivman'),
        StringStruct(u'LegalCopyright', u'Copyright © 2015 Yubico'),
        StringStruct(u'OriginalFilename', u'%(exe_name)s'),
        StringStruct(u'ProductName', u'YubiKey PIV Manager'),
        StringStruct(u'ProductVersion', u'%(ver_str)s')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1252])])
  ]
)""" % {
            'ver_tup': ver_tup,
            'ver_str': ver_str,
            'exe_name': '%s.exe' % NAME
        })

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=NAME if not WIN else '%s.exe' % NAME,
          debug=False,
          strip=None,
          upx=True,
          console=False,
          append_pkg=not OSX,
          version=VERSION,
          icon=ICON)

pfx_pass = ""

if WIN:
    if not os.path.isfile("yubico.pfx"):
        print "yubico.pfx not found, not signing executable!"
    else:
        pfx_pass = getpass('Enter password for PFX file: ')
        os.system("signtool.exe sign /f yubico.pfx /p %s /t http://timestamp.verisign.com/scripts/timstamp.dll \"%s\"" %
                 (pfx_pass, exe.name))

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=NAME)

# Create .app for OSX
if OSX:
    app = BUNDLE(coll,
                 name="%s.app" % NAME,
                 version=ver_str,
                 icon=ICON)

    from shutil import copy2 as copy
    copy('resources/qt.conf', 'dist/%s.app/Contents/Resources/' % NAME)

# Create Windows installer
if WIN:
    os.system('makensis.exe -D"PIVMAN_VERSION=%s" resources/pivman.nsi' % ver_str)
    installer = "dist/yubikey-piv-manager-%s-win.exe" % ver_str
    os.system("signtool.exe sign /f yubico.pfx /p %s /t http://timestamp.verisign.com/scripts/timstamp.dll \"%s\"" %
             (pfx_pass, installer))
    print "Installer created: %s" % installer
