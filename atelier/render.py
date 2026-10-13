"""Rendus par les outils externes : MuseScore (batch), LilyPond, Audiveris (OMR), FluidSynth (audio)."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
from .env import find


def _need(tool: str) -> str:
    p = find(tool)
    if not p:
        raise SystemExit(f"{tool} introuvable : lancez `python -m atelier env` et tools/setup-*.")
    return p


def run(cmd: list[str], timeout: int = 900) -> int:
    print("$", " ".join(f'"{c}"' if " " in c else c for c in cmd), file=sys.stderr)
    return subprocess.run(cmd, timeout=timeout).returncode


def musescore_export(src: str | Path, out: str | Path, parts: bool = False) -> int:
    """`out` fixe le format par son extension (.pdf .musicxml .mxl .mid .mp3 .wav .png .svg).
    parts=True exporte aussi chaque partie séparée (MuseScore 4 : --export-score-parts, PDF)."""
    ms = _need("musescore")
    cmd = [ms, "-o", str(out), str(src)]
    if parts:
        cmd.insert(1, "--export-score-parts")
    return run(cmd)


def lilypond_compile(src: str | Path, outdir: str | Path | None = None, extra: list[str] | None = None) -> int:
    ly = _need("lilypond")
    cmd = [ly, "-dno-point-and-click"]
    if outdir:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        cmd += ["-o", str(Path(outdir) / Path(src).stem)]
    cmd += (extra or []) + [str(src)]
    return run(cmd, timeout=1800)


def audiveris_batch(inputs: list[str | Path], outdir: str | Path) -> int:
    av = _need("audiveris")
    Path(outdir).mkdir(parents=True, exist_ok=True)
    return run([av, "-batch", "-export", "-output", str(outdir), *map(str, inputs)], timeout=3600)


def fluidsynth_render(midi: str | Path, soundfont: str | Path, out_wav: str | Path, rate: int = 44100) -> int:
    fs = _need("fluidsynth")
    return run([fs, "-ni", "-r", str(rate), "-F", str(out_wav), str(soundfont), str(midi)])


def main(args) -> int:
    if args.tool == "musescore":
        return musescore_export(args.src, args.out, args.parts)
    if args.tool == "lilypond":
        return lilypond_compile(args.src, args.out)
    if args.tool == "audiveris":
        return audiveris_batch([args.src], args.out or "work/omr")
    if args.tool == "fluidsynth":
        if not args.soundfont:
            raise SystemExit("--soundfont requis (ex. VSCO 2 CE .sf2)")
        return fluidsynth_render(args.src, args.soundfont, args.out or Path(args.src).with_suffix(".wav"))
    raise SystemExit(f"outil inconnu : {args.tool}")
