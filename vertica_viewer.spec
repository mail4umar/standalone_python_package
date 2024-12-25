# framework_v2.spec
a = Analysis(
    ['framework_v2.py'],
    pathex=['.'],
    binaries=[],
    # datas=[
    #     ('C:\\Users\\ughumman\\AppData\\Local\\anaconda3\\envs\\app\\Lib\\site-packages\\vertica_highcharts\\highcharts\\templates', 'vertica_highcharts/highcharts/templates'),
    # ],
    data = [],
    # hiddenimports=['verticapy', 'PyQt6', 'PyQt6.QtWebEngineWidgets', 'vertica_highcharts', 'vertica_highcharts.highcharts'],
    hiddenimports=['verticapy', 'PyQt6', 'PyQt6.QtWebEngineWidgets'],
    excludes=['vertica_highcharts'],
    cipher=None
)
# from PyInstaller.utils.crypto import generate_key
# a = Analysis(
#     ['framework_v2.py'],
#     pathex=['.'],
#     binaries=[],
#     datas=[],
#     hiddenimports=['verticapy', 'PyQt6', 'PyQt6.QtWebEngineWidgets'],
#     cipher=generate_key()
# )
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
    console=False,
    onefile=True
)