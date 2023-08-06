# -*- mode: python -*-
a = Analysis(['depot_downloader.py'],
             hiddenimports=['greenlet', 'google', 'google.protobuf'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='depotdownloader.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
