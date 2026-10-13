"""python -m atelier <commande> ... — voir README."""
from __future__ import annotations
import argparse, sys
from . import __version__


def build() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="atelier", description="Atelier d'arrangement : chaîne libre scriptée.")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("env", help="état des outils externes et modules Python")

    a = sub.add_parser("analyse", help="structure, tonalités par fenêtre, tessitures par partie")
    a.add_argument("file"); a.add_argument("--window", type=int, default=8); a.add_argument("--json", action="store_true")

    e = sub.add_parser("extract", help="mesures a–b (parties choisies, transposition) -> MusicXML")
    e.add_argument("file"); e.add_argument("start", type=int); e.add_argument("end", type=int)
    e.add_argument("--parts", nargs="*"); e.add_argument("--transpose", type=int, default=0); e.add_argument("--out")

    g = sub.add_parser("engrave", help="MusicXML/MEI/ABC -> SVG (Verovio)")
    g.add_argument("file"); g.add_argument("--out"); g.add_argument("--scale", type=int, default=40); g.add_argument("--all-pages", action="store_true")

    r = sub.add_parser("render", help="musescore | lilypond | audiveris | fluidsynth")
    r.add_argument("tool", choices=["musescore", "lilypond", "audiveris", "fluidsynth"]); r.add_argument("src"); r.add_argument("--out")
    r.add_argument("--parts", action="store_true", help="MuseScore : exporter aussi les parties"); r.add_argument("--soundfont")

    c = sub.add_parser("check", help="contrôles du matériel (mesures, tessitures, repères, cues)")
    c.add_argument("file"); c.add_argument("--marks-every", type=int, default=12); c.add_argument("--require-marks", type=int, nargs="*")
    c.add_argument("--json", action="store_true")

    m = sub.add_parser("medley", help="ordre, transitions et minutage d'un medley depuis un plan JSON/YAML")
    m.add_argument("plan"); m.add_argument("--json", action="store_true")

    d = sub.add_parser("dossier", help="fusionner des PDF en un dossier numéroté")
    d.add_argument("pdfs", nargs="+"); d.add_argument("--out", required=True); d.add_argument("--title"); d.add_argument("--no-numbers", action="store_true")
    return ap


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):  # consoles Windows en cp1252 : forcer l'UTF-8
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    args = build().parse_args(argv)
    if args.cmd == "env":
        from .env import print_report; return print_report()
    mod = {"analyse": "analyse", "extract": "extract", "engrave": "engrave", "render": "render",
           "check": "check", "medley": "medley", "dossier": "dossier"}[args.cmd]
    return __import__(f"atelier.{mod}", fromlist=["main"]).main(args)


if __name__ == "__main__":
    sys.exit(main())
