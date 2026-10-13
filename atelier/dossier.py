"""Assembler le matériel : fusion de PDF, page de garde, numérotation (PyMuPDF)."""
from __future__ import annotations
from pathlib import Path
import pymupdf


def merge(pdfs: list[str | Path], out: str | Path, title: str | None = None, number: bool = True) -> Path:
    doc = pymupdf.open()
    if title:
        page = doc.new_page(width=595, height=842)
        page.insert_text((60, 300), title, fontsize=24, fontname="Times-Bold")
        page.insert_text((60, 340), "\n".join(Path(p).stem for p in pdfs), fontsize=11, fontname="Times-Roman")
    for p in pdfs:
        with pymupdf.open(p) as src:
            doc.insert_pdf(src)
    if number:
        for i, page in enumerate(doc, start=1):
            if title and i == 1:
                continue
            page.insert_text((page.rect.width / 2 - 8, page.rect.height - 20), str(i), fontsize=9, fontname="Helvetica")
    out = Path(out)
    doc.save(str(out))
    doc.close()
    return out


def main(args) -> int:
    print(merge(args.pdfs, args.out, args.title, not args.no_numbers))
    return 0
