"""Tessitures pratiques (notes ÉCRITES) pour un orchestre d'étudiants, et transpositions.

`transpose` = demi-tons à ajouter à la note écrite pour obtenir la note réelle.
Les bornes « confort » servent aux contrôles ; les bornes « limite » déclenchent une erreur.
"""
from __future__ import annotations
import re

RANGES = {
    #  clé : (mots-clés de nom de partie), confort (bas, haut), limite (bas, haut), transposition
    "flute":       {"match": ["flute", "flûte", "fl."],           "comfort": ("D4", "A6"),  "limit": ("C4", "C7"),  "transpose": 0},
    "piccolo":     {"match": ["piccolo", "picc"],                 "comfort": ("E4", "A6"),  "limit": ("D4", "C7"),  "transpose": 12},
    "oboe":        {"match": ["oboe", "hautbois", "ob."],          "comfort": ("C4", "D6"),  "limit": ("Bb3", "F6"), "transpose": 0},
    "clarinet_bb": {"match": ["clarinet", "clarinette", "cl."],   "comfort": ("E3", "E6"),  "limit": ("E3", "G6"),  "transpose": -2},
    "clarinet_a":  {"match": ["clarinet in a", "clarinette en la", "cl. (la)"], "comfort": ("E3", "E6"), "limit": ("E3", "G6"), "transpose": -3},
    "bassoon":     {"match": ["bassoon", "basson", "fagott", "fg.", "bn."], "comfort": ("C2", "C5"), "limit": ("Bb1", "Eb5"), "transpose": 0},
    "horn_f":      {"match": ["horn", "cor", "hn."],              "comfort": ("C3", "G5"),  "limit": ("F2", "C6"),  "transpose": -7},
    "trumpet_bb":  {"match": ["trumpet", "trompette", "tpt", "tr."], "comfort": ("A3", "G5"), "limit": ("F#3", "C6"), "transpose": -2},
    "trombone":    {"match": ["trombone", "tbn", "trb"],          "comfort": ("A2", "F4"),  "limit": ("E2", "Bb4"), "transpose": 0},
    "timpani":     {"match": ["timpani", "timbales", "timp"],     "comfort": ("F2", "F3"),  "limit": ("D2", "A3"),  "transpose": 0},
    "violin":      {"match": ["violin", "violon", "vl.", "vn."],  "comfort": ("G3", "E6"),  "limit": ("G3", "B6"),  "transpose": 0},
    "viola":       {"match": ["viola", "alto", "va."],            "comfort": ("C3", "A5"),  "limit": ("C3", "E6"),  "transpose": 0},
    "cello":       {"match": ["cello", "violoncelle", "vc."],     "comfort": ("C2", "A4"),  "limit": ("C2", "G5"),  "transpose": 0},
    "bass":        {"match": ["double bass", "contrabass", "contrebasse", "cb.", "kb."], "comfort": ("E2", "D4"), "limit": ("E2", "G4"), "transpose": -12},
    "harp":        {"match": ["harp", "harpe"],                   "comfort": ("C1", "G7"),  "limit": ("C1", "G7"),  "transpose": 0},
    "piano":       {"match": ["piano", "pf."],                    "comfort": ("A0", "C8"),  "limit": ("A0", "C8"),  "transpose": 0},
}


def guess(part_name: str) -> str | None:
    """Devine l'instrument depuis le nom de partie (fr/en/it, abréviations)."""
    n = (part_name or "").lower()
    n = re.sub(r"\s+", " ", n)
    # ordre : les clés les plus spécifiques d'abord
    # « violoncelle » contient « violon » et « contrebasse » contient « basse » : les plus longs d'abord
    for key in ["clarinet_a", "piccolo", "bass", "cello", "trombone", "trumpet_bb", "timpani", "bassoon", "clarinet_bb",
                "oboe", "flute", "horn_f", "viola", "violin", "harp", "piano"]:
        if any(m in n for m in RANGES[key]["match"]):
            return key
    return None
