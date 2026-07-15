from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path(SPECPATH)

playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all(
    "playwright"
)

uvicorn_datas, uvicorn_binaries, uvicorn_hiddenimports = collect_all(
    "uvicorn"
)


a = Analysis(
    ["launcher.py"],
    pathex=[str(project_root)],
    binaries=playwright_binaries + uvicorn_binaries,
    datas=[
        (
            str(project_root / "playwright-browsers"),
            "playwright-browsers",
        ),
        (
            str(project_root / "src" / "templates"),
            "src/templates",
        ),
        (
            str(project_root / "src" / "static"),
            "src/static",
        ),
        *playwright_datas,
        *uvicorn_datas,
    ],

    hiddenimports=[
    *playwright_hiddenimports,
    *uvicorn_hiddenimports,

    "src",
    "src.web",
    "src.api",
    "src.api.scans",
    "src.services",
    "src.services.scan_service",
    "src.crawler",
    "src.crawler.browser_extractor",
    "src.checker",
    "src.checker.link_checker",

    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)


pyz = PYZ(a.pure)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LinkChecker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LinkChecker",
)