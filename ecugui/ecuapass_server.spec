# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['ecuapass_server.py'],
    pathex=[],
    binaries=[],
    datas=[('images/*.png', 'images/'),
	       ('ecuapassdocs/resources/data-cartaportes/*.txt', "."),
	       ('ecuapassdocs/resources/data-declaracion/*.txt', "."),
	       ('ecuapassdocs/resources/data-manifiestos/*.txt', "."),
	       ('ecuapassdocs/resources/docs/*.txt', "."),
	       ('ecuapassdocs/resources/docs/*.pdf', "."),
	       ('ecuapassdocs/resources/docs/*.png', ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ecuapass_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
