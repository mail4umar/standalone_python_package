# framework_v2.spec
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all vertica_highcharts related files
highcharts_data = collect_data_files('vertica_highcharts')
highcharts_imports = collect_submodules('vertica_highcharts')

a = Analysis(
    ['framework_v2.py'],
    pathex=['.'],
    binaries=[],
    datas=highcharts_data,
    hiddenimports=[
        'verticapy',
        'PyQt6',
        'PyQt6.QtWebEngineWidgets',
        'vertica_highcharts',
        'vertica_highcharts.highcharts',
        *highcharts_imports
    ],
    cipher=None
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VerticaViewer',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,  # Set to True temporarily for debugging
    onefile=True
)