"""Localisation des outils externes et rapport d'environnement."""
from __future__ import annotations
import os, shutil, subprocess, sys
from pathlib import Path

CANDIDATES = {
    "musescore": ["mscore", "musescore", "MuseScore4", "mscore4portable",
                  r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
                  "/Applications/MuseScore 4.app/Contents/MacOS/mscore", "/usr/bin/mscore4portable"],
    "lilypond": ["lilypond", r"C:\Program Files\LilyPond\usr\bin\lilypond.exe", r"C:\Program Files (x86)\LilyPond\usr\bin\lilypond.exe",
                 "/Applications/LilyPond.app/Contents/Resources/bin/lilypond"],
    "musicxml2ly": ["musicxml2ly", r"C:\Program Files\LilyPond\usr\bin\musicxml2ly.py"],
    "audiveris": ["audiveris", "Audiveris", r"C:\Program Files\Audiveris\Audiveris.exe", r"C:\Program Files\Audiveris\bin\Audiveris.bat"],
    "fluidsynth": ["fluidsynth", r"C:\Program Files\FluidSynth\bin\fluidsynth.exe", r"C:\tools\fluidsynth\bin\fluidsynth.exe"],
    "pdfcpu": ["pdfcpu"],
    "qpdf": ["qpdf"],
    "ffmpeg": ["ffmpeg"],
    "git": ["git"],
}
PY_MODULES = ["music21", "verovio", "pymupdf", "mido", "pytest"]


def find(tool: str) -> str | None:
    """Chemin de l'outil, par variable d'environnement ATELIER_<TOOL>, PATH, puis emplacements usuels."""
    env = os.environ.get(f"ATELIER_{tool.upper()}")
    if env and Path(env).exists():
        return env
    for c in CANDIDATES.get(tool, [tool]):
        p = shutil.which(c)
        if p:
            return p
        if Path(c).exists():
            return c
    return None


def version(tool: str, path: str) -> str:
    flag = {"musescore": "--version", "lilypond": "--version", "audiveris": "-help", "fluidsynth": "--version",
            "pdfcpu": "version", "qpdf": "--version", "ffmpeg": "-version", "git": "--version", "musicxml2ly": "--version"}.get(tool, "--version")
    try:
        out = subprocess.run([path, flag], capture_output=True, text=True, timeout=20)
        line = (out.stdout or out.stderr).strip().splitlines()
        return line[0][:70] if line else "?"
    except Exception as e:  # noqa: BLE001
        return f"? ({e.__class__.__name__})"


def report() -> dict:
    tools = {}
    for t in CANDIDATES:
        p = find(t)
        tools[t] = {"path": p, "version": version(t, p) if p else None}
    mods = {}
    for m in PY_MODULES:
        try:
            mod = __import__(m)
            mods[m] = getattr(mod, "__version__", None) or getattr(mod, "VersionBind", None) or "ok"
        except Exception:  # noqa: BLE001
            mods[m] = None
    return {"python": sys.version.split()[0], "tools": tools, "modules": mods}


def print_report() -> int:
    r = report()
    print(f"Python {r['python']}")
    missing = 0
    for t, info in r["tools"].items():
        if info["path"]:
            print(f"  [ok]      {t:12s} {info['version']}  ({info['path']})")
        else:
            print(f"  [absent]  {t:12s} voir tools/setup-*.{'ps1' if os.name == 'nt' else 'sh'}")
            missing += 1
    for m, v in r["modules"].items():
        print(f"  [{'ok' if v else 'absent'}]{' ' * (6 if v else 2)}python:{m:10s} {v or ''}")
        missing += 0 if v else 1
    return 0 if missing == 0 else 1
