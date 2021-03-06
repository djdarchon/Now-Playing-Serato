# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SeratoNowPlaying.py'],
             pathex=['/Users/miranda/Documents/GitHub/Now-Playing-Serato/Serato-Now-Playing'],
             binaries=[],
             datas=[('bin/icon.ico', './bin')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='SeratoNowPlaying',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='resources/seratoPlaying.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SeratoNowPlaying')
app = BUNDLE(coll,
             name='SeratoNowPlaying.app',
             icon='resources/seratoPlaying.icns',
             bundle_identifier=None, 
             info_plist={
                'LSUIElement': True
             })
