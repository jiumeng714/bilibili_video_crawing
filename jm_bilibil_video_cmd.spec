# -*- mode: python ; coding: utf-8 -*-
#
# 和 jm_bilibil_video.spec 完全一样，只是 console=True：
# 打包出来会同时显示控制台窗口，方便看到报错信息（对应根目录的 jm_cmd_B站视频封面爬取.exe）


block_cipher = None


a = Analysis(
    ['jm_bilibil_video.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    name='jm_cmd_B站视频封面爬取',
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
