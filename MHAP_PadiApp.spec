# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define excluded modules
excluded_modules = [
    'matplotlib', 'PIL', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
    'wx', 'IPython', 'numpy.random', 'scipy', 'cv2', 'notebook',
    'pytest', 'unittest', 'doctest', 'pygame'
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'selenium.webdriver',
        'pandas',
        'openpyxl'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files from the bundle
def remove_from_list(base, remove):
    for rem in remove:
        base_list = a.binaries if base == 'bin' else a.datas
        for item in base_list[:]:
            if rem in item[0]:
                base_list.remove(item)

remove_from_list('bin', ['_test', 'test', 'tests'])
remove_from_list('data', ['matplotlib', 'mpl-data', 'tk/demos', 'tk/images', 'tk/msgs'])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MHAP_PadiApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon.ico'
)