"""Extraire des mesures, choisir des parties, transposer -> MusicXML."""
from __future__ import annotations
from pathlib import Path
import music21 as m21
from .analyse import load


def extract(path: str | Path, start: int, end: int, parts: list[str] | None = None, transpose: int = 0,
            out: str | Path | None = None) -> Path:
    s = load(path)
    sel = s.measures(start, end)
    if parts:
        import re
        from .ranges import guess
        wanted = [p.lower() for p in parts]

        def match(p):
            name = (p.partName or "").lower()
            words = set(re.split(r"[\s.,;:()\-]+", name))
            return any(w == name or w in words or w == guess(name) for w in wanted)
        keep = [p for p in sel.parts if match(p)]
        if not keep:
            raise SystemExit(f"aucune partie ne correspond à {parts} ; parties : {[p.partName for p in s.parts]}")
        sel = m21.stream.Score(keep)
    if transpose:
        sel = sel.transpose(transpose)
    out = Path(out or f"{Path(path).stem}_{start}-{end}{'_t%+d' % transpose if transpose else ''}.musicxml")
    sel.write("musicxml", fp=str(out))
    return out


def main(args) -> int:
    out = extract(args.file, args.start, args.end, args.parts, args.transpose, args.out)
    print(out)
    return 0
