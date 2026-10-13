"""Contrôles automatiques du matériel : cohérence des mesures, tessitures, repères, mesures vides.

Sortie : liste de problèmes (niveau, partie, mesure, message). Code retour 1 si une erreur.
"""
from __future__ import annotations
import json
from pathlib import Path
import music21 as m21
from .analyse import load
from .ranges import RANGES, guess


def check(path: str | Path, marks_every: int = 12, require_marks_at: list[int] | None = None) -> list[dict]:
    s = load(path)
    issues: list[dict] = []
    counts = {p.partName or p.id: len(p.getElementsByClass(m21.stream.Measure)) for p in s.parts}
    if len(set(counts.values())) > 1:
        issues.append({"level": "error", "part": "*", "measure": None,
                       "msg": f"nombre de mesures différent entre les parties : {counts}"})
    p0 = s.parts[0]
    n = len(p0.getElementsByClass(m21.stream.Measure))
    marks = sorted(m.number for m in p0.getElementsByClass(m21.stream.Measure) if m.getElementsByClass(m21.expressions.RehearsalMark))
    if n > marks_every and not marks:
        issues.append({"level": "warning", "part": "*", "measure": None, "msg": f"aucun repère de répétition sur {n} mesures (un tous les {marks_every} conseillé)"})
    for m_req in (require_marks_at or []):
        if m_req not in marks:
            issues.append({"level": "error", "part": "*", "measure": m_req, "msg": "repère attendu à cette jonction, absent"})
    for p in s.parts:
        name = p.partName or p.id or "?"
        inst = guess(name)
        if not inst:
            issues.append({"level": "info", "part": name, "measure": None, "msg": "instrument non reconnu : tessiture non contrôlée"})
        else:
            lim_lo, lim_hi = (m21.pitch.Pitch(x) for x in RANGES[inst]["limit"])
            com_lo, com_hi = (m21.pitch.Pitch(x) for x in RANGES[inst]["comfort"])
            for nt in p.recurse().notes:
                mnum = nt.getContextByClass(m21.stream.Measure)
                mnum = mnum.number if mnum is not None else None
                for pt in (nt.pitches if nt.isChord else [nt.pitch]):
                    if pt.ps < lim_lo.ps or pt.ps > lim_hi.ps:
                        issues.append({"level": "error", "part": name, "measure": mnum, "msg": f"{pt.nameWithOctave} hors limite ({RANGES[inst]['limit'][0]}–{RANGES[inst]['limit'][1]})"})
                    elif pt.ps < com_lo.ps or pt.ps > com_hi.ps:
                        issues.append({"level": "warning", "part": name, "measure": mnum, "msg": f"{pt.nameWithOctave} hors confort ({RANGES[inst]['comfort'][0]}–{RANGES[inst]['comfort'][1]})"})
        # longues plages de silence : utile pour placer les cues
        silent = 0
        for m in p.getElementsByClass(m21.stream.Measure):
            if not m.recurse().notes:
                silent += 1
            else:
                if silent >= 16:
                    issues.append({"level": "info", "part": name, "measure": m.number, "msg": f"entrée après {silent} mesures de silence : prévoir une note de repère (cue)"})
                silent = 0
    return issues


def main(args) -> int:
    issues = check(args.file, args.marks_every, args.require_marks)
    if args.json:
        print(json.dumps(issues, ensure_ascii=False, indent=1))
    else:
        for i in issues:
            print(f"[{i['level']:7s}] {i['part'][:24]:24s} mes. {str(i['measure']):>4s}  {i['msg']}")
        errors = sum(1 for i in issues if i["level"] == "error")
        print(f"{len(issues)} remarques, {errors} erreurs")
    return 1 if any(i["level"] == "error" for i in issues) else 0
