"""Génère les plans de medley de démonstration (examples/medleys/*.json) à partir du répertoire.

Chaque plan contient la Pavane de Ravel et Tico-Tico (pièces demandées), vise 30 minutes de musique
continue (ponts compris) et ne puise que dans examples/repertoire.json.
Usage : python examples/make_medleys.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "medleys"
OUT.mkdir(exist_ok=True)

PLANS = {
    "1-programme-1-en-medley": {
        "name": "Programme 1 « Deux pavanes » converti en medley",
        "pieces": [("faure-pavane", 4.5, "first"), ("bizet-adagietto", 2.5), ("massenet-meditation", 4.5), ("faure-sicilienne", 3),
                   ("bizet-entracte3", 2.5), ("elgar-salut", 3), ("ravel-pavane", 5.5), ("tico-tico", 3, "last")],
    },
    "1b-programme-1-corrige": {
        "name": "Programme 1 corrigé : une danse rapide remplace l'Entr'acte",
        "pieces": [("faure-pavane", 4.5, "first"), ("bizet-adagietto", 2.5), ("massenet-meditation", 4.5), ("faure-sicilienne", 3),
                   ("bizet-aragonaise", 2), ("elgar-salut", 3), ("ravel-pavane", 5.5), ("tico-tico", 3, "last"), ("boccherini-minuetto", 2.5)],
    },
    "2-danses-du-monde": {
        "name": "Danses du monde",
        "pieces": [("brahms-hongroise5", 2.5, "first"), ("bizet-habanera", 2.5), ("bizet-aragonaise", 2), ("grieg-anitra", 3),
                   ("tchaik-valse-serenade", 3), ("boccherini-minuetto", 2.5), ("strauss-pizzicato", 2.5), ("ravel-pavane", 4.5),
                   ("joplin-entertainer", 2.5), ("gardel-cabeza", 2.5), ("tico-tico", 3, "last")],
    },
    "3-paris-1900": {
        "name": "Paris 1900",
        "pieces": [("bizet-carmen-prelude", 2, "first"), ("faure-pavane", 3.5), ("satie-gymnopedie", 2.5), ("bizet-aragonaise", 2),
                   ("faure-sicilienne", 3), ("offenbach-barcarolle", 3), ("debussy-clair-de-lune", 3.5), ("saint-saens-cygne", 2.5),
                   ("ravel-pavane", 5), ("tico-tico", 3, "last")],
    },
    "4-contes-et-ballets": {
        "name": "Contes et ballets",
        "pieces": [("grieg-morning", 3, "first"), ("tchaik-mirlitons", 2), ("grieg-anitra", 2.5), ("tchaik-arabe", 2.5),
                   ("tchaik-trepak", 1), ("mendelssohn-notturno", 3), ("tchaik-dragee", 2), ("ravel-pavane", 4.5),
                   ("grieg-mountain-king", 2.5), ("tchaik-valse-fleurs", 4), ("tico-tico", 3, "last")],
    },
    "5-effectif-de-base-seul": {
        "name": "Effectif de base seul (aucun instrument en plus)",
        "pieces": [("mozart-nachtmusik", 3, "first"), ("schubert-rosamunde", 3), ("grieg-last-spring", 3.5), ("elgar-matin", 3),
                   ("boccherini-minuetto", 2.5), ("tchaik-valse-serenade", 3), ("mascagni-intermezzo", 3), ("ravel-pavane", 5),
                   ("tico-tico", 3, "last")],
    },
    "6-nina-soliste": {
        "name": "Nina soliste, et chacun son tour",
        "pieces": [("schubert-ballet", 3, "first"), ("faure-berceuse", 3.5), ("grieg-ase", 2), ("massenet-meditation", 5),
                   ("mozart-romanze", 3), ("bizet-aragonaise", 2), ("ravel-pavane", 5), ("gardel-cabeza", 2.5), ("tico-tico", 3, "last")],
    },
}

for stem, p in PLANS.items():
    pieces = []
    for item in p["pieces"]:
        ref, minutes, *fixed = item
        d = {"ref": ref, "minutes": minutes}
        if fixed:
            d["fixed"] = fixed[0]
        pieces.append(d)
    spec = {"name": p["name"], "repertoire": "../repertoire.json", "target_minutes": 30, "tolerance": 1.5,
            "base_forces": ["2 fl", "2 hb", "2 cl", "2 bn", "2 cors", "harpe ou piano", "cordes"], "pieces": pieces}
    (OUT / f"{stem}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(OUT / f"{stem}.json")
