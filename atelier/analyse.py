"""Analyse d'une partition (MusicXML, MIDI, MEI, kern, ABC) : structure, tonalités, tessitures."""
from __future__ import annotations
import json
from pathlib import Path
import music21 as m21
from .ranges import RANGES, guess


def load(path: str | Path) -> m21.stream.Score:
    s = m21.converter.parse(str(path), quantizePost=str(path).lower().endswith((".mid", ".midi")))
    return s if isinstance(s, m21.stream.Score) else m21.stream.Score([s])


def key_map(score: m21.stream.Score, window: int = 8) -> list[dict]:
    """Tonalité estimée par fenêtres de `window` mesures (Krumhansl)."""
    out = []
    numbers = [m.number for m in score.parts[0].getElementsByClass(m21.stream.Measure)] if score.parts else []
    for i in range(0, len(numbers), window):
        start, end = numbers[i], numbers[min(i + window - 1, len(numbers) - 1)]
        try:
            k = score.measures(start, end).analyze("key")
            out.append({"from": start, "to": end, "key": f"{k.tonic.name} {k.mode}", "confidence": round(k.correlationCoefficient, 2)})
        except Exception:  # noqa: BLE001
            out.append({"from": start, "to": end, "key": None, "confidence": None})
    return out


def part_info(part: m21.stream.Part) -> dict:
    name = part.partName or part.id or "?"
    inst = guess(name)
    notes = list(part.recurse().notes)
    pitches = [p for n in notes for p in (n.pitches if n.isChord else [n.pitch])]
    lo = min(pitches, key=lambda p: p.ps) if pitches else None
    hi = max(pitches, key=lambda p: p.ps) if pitches else None
    measures = part.getElementsByClass(m21.stream.Measure)
    fastest = min((e.quarterLength for e in part.recurse().notesAndRests if e.quarterLength > 0), default=None)
    info = {"part": name, "instrument": inst, "measures": len(measures), "notes": len(notes),
            "low": lo.nameWithOctave if lo else None, "high": hi.nameWithOctave if hi else None,
            "fastest_quarterLength": fastest}
    if inst and pitches:
        r = RANGES[inst]
        lim_lo, lim_hi = m21.pitch.Pitch(r["limit"][0]), m21.pitch.Pitch(r["limit"][1])
        com_lo, com_hi = m21.pitch.Pitch(r["comfort"][0]), m21.pitch.Pitch(r["comfort"][1])
        info["out_of_limit"] = sum(1 for p in pitches if p.ps < lim_lo.ps or p.ps > lim_hi.ps)
        info["out_of_comfort"] = sum(1 for p in pitches if p.ps < com_lo.ps or p.ps > com_hi.ps)
    return info


def structure(score: m21.stream.Score) -> dict:
    p0 = score.parts[0]
    ts = [(m.number, m.timeSignature.ratioString) for m in p0.getElementsByClass(m21.stream.Measure) if m.timeSignature]
    tempi = [(round(float(t.offset), 2), t.number) for t in score.flatten().getElementsByClass(m21.tempo.MetronomeMark)]
    marks = [(m.number, str(rm.content)) for m in p0.getElementsByClass(m21.stream.Measure) for rm in m.getElementsByClass(m21.expressions.RehearsalMark)]
    return {"measures": len(p0.getElementsByClass(m21.stream.Measure)), "time_signatures": ts[:20], "tempi": tempi[:20], "rehearsal_marks": marks}


def analyse(path: str | Path, window: int = 8) -> dict:
    s = load(path)
    return {"file": str(path), "structure": structure(s), "keys": key_map(s, window), "parts": [part_info(p) for p in s.parts]}


def main(args) -> int:
    rep = analyse(args.file, args.window)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    st = rep["structure"]
    print(f"{rep['file']}: {st['measures']} mesures ; mesures {st['time_signatures'][:4]} ; tempi {st['tempi'][:4]} ; repères {st['rehearsal_marks'][:10]}")
    print("Tonalités par fenêtre :", ", ".join(f"{k['from']}–{k['to']} {k['key']} ({k['confidence']})" for k in rep["keys"]))
    print(f"{'partie':28s} {'instr.':12s} {'mes.':>5s} {'notes':>6s} {'bas':>5s} {'haut':>5s} {'hors':>5s}")
    for p in rep["parts"]:
        print(f"{p['part'][:28]:28s} {str(p['instrument']):12s} {p['measures']:5d} {p['notes']:6d} {str(p['low']):>5s} {str(p['high']):>5s} {str(p.get('out_of_limit', '')):>5s}")
    return 0
