"""Graver un fichier (MusicXML/MEI/ABC/kern) en SVG avec Verovio, sans ouvrir d'éditeur."""
from __future__ import annotations
from pathlib import Path
import verovio

DEFAULT = {"pageWidth": 2200, "pageHeight": 60000, "scale": 40, "adjustPageHeight": True, "breaks": "auto",
           "footer": "none", "header": "none", "mnumInterval": 1, "svgViewBox": True, "spacingStaff": 6, "spacingSystem": 7}


def engrave(path: str | Path, out: str | Path | None = None, scale: int = 40, all_pages: bool = False) -> list[Path]:
    tk = verovio.toolkit()
    tk.setOptions({**DEFAULT, "scale": scale})
    tk.loadData(Path(path).read_text(encoding="utf-8"))
    out = Path(out or Path(path).with_suffix(".svg"))
    files = []
    pages = tk.getPageCount() if all_pages else 1
    for i in range(1, pages + 1):
        target = out if pages == 1 else out.with_name(f"{out.stem}-p{i}{out.suffix}")
        target.write_text(tk.renderToSVG(i), encoding="utf-8")
        files.append(target)
    return files


def main(args) -> int:
    for f in engrave(args.file, args.out, args.scale, args.all_pages):
        print(f)
    return 0
