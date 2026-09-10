import sys
sys.setrecursionlimit(3000)

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        # Selenium Core
        "selenium",
        "selenium.webdriver",
        "selenium.webdriver.chrome",
        "selenium.webdriver.chrome.webdriver",
        "selenium.webdriver.chrome.options",
        "selenium.webdriver.chrome.service",

        # Selenium Common
        "selenium.webdriver.common",
        "selenium.webdriver.common.by",
        "selenium.webdriver.common.keys",
        "selenium.webdriver.common.action_chains",

        # Selenium Support
        "selenium.webdriver.support",
        "selenium.webdriver.support.ui",
        "selenium.webdriver.support.expected_conditions",

        # Selenium Exceptions
        "selenium.common.exceptions",

        # WebDriver Manager (kalau dipakai)
        "webdriver_manager",
        "webdriver_manager.chrome",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "torchvision",
        "tensorflow",
        "tensorflow_datasets",
        "matplotlib",
        "scipy",
        "numba",
        "llvmlite",
        "pyarrow",
        "IPython",
        "jupyter",
        "zmq",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    exclude_binaries=False,
    name='MahdiPDFStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

