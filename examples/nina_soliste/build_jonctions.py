"""Dossier de vérification du medley « Nina soliste » : jonctions en réduction pour piano.

Pour chaque jonction : fin de l'extrait A (source fiable si disponible) + pont esquissé + début de l'extrait B.
Une source absente est remplacée par une mesure vide portant un texte « source à fournir ».
Sorties (dans OUT) : jNN.musicxml, jNN.mid ; le rendu PDF (MuseScore) et WAV (FluidSynth) est fait par make_dossier.sh.

Usage : python build_jonctions.py SRC_DIR OUT_DIR
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import music21 as m21

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "mozart": {"file": "mutopia/MozartWA-KV525-mov-02.mid", "label": "Mozart, Romanze (Mutopia, quatuor à cordes)", "reliable": True},
    "grieg": {"file": "mutopia/aasesdeath.mid", "label": "Grieg, La mort d'Åse (Mutopia, cordes)", "reliable": True},
    "massenet": {"file": "bm-73032.mid", "label": "Massenet, Méditation (MIDI bitmidi n° 73032, orchestre, non vérifié)", "reliable": False},
}

# pont : liste de mesures ; chaque mesure = liste d'accords (basse, [aigus], durée en noires)
JONCTIONS = [
    {"id": "j1", "title": "Schubert, Ballet n° 2 → Mozart, Romanze", "a": None, "a_label": "Schubert, Ballet n° 2 : fin",
     "b": ("mozart", 1, 4), "tempo_a": 72, "tempo_b": 60, "kind": "pont de 2 mesures, sol majeur → do majeur",
     "bridge": [[("G2", ["B3", "D4", "G4"], 2), ("B2", ["D4", "G4"], 2)], [("G2", ["B3", "D4", "F4", "G4"], 4, "fermata")]],
     "questions": ["Le ritenuto sur sol⁷ suffit-il, ou faut-il un point d'orgue plus long avant la Romanze ?", "Qui joue le pont : bois seuls (couleur Schubert) ou cordes (couleur Mozart) ?"]},
    {"id": "j2", "title": "Mozart, Romanze → Bizet, Aragonaise", "a": ("mozart", 35, 38), "b": None, "b_label": "Bizet, Carmen, Aragonaise : début",
     "tempo_a": 60, "tempo_b": 132, "kind": "pont de 2 mesures, do majeur → ré mineur, puis nouveau départ rapide",
     "bridge": [[("C3", ["C4", "E4", "G4"], 2), ("C#3", ["E4", "G4", "B-4"], 2)], [("A2", ["C#4", "E4", "G4", "A4"], 4, "fermata")]],
     "questions": ["Le contraste Romanze (♩=60) → Aragonaise (♩=132) : point d'orgue sur la⁷ puis départ du tambourin, ou enchaînement attaca ?"]},
    {"id": "j3", "title": "Bizet, Aragonaise → Gardel, Por una cabeza", "a": None, "a_label": "Bizet, Aragonaise : fin", "b": None, "b_label": "Gardel, Por una cabeza : début",
     "tempo_a": 132, "tempo_b": 112, "kind": "pont de 2 mesures, ré mineur → la mineur",
     "bridge": [[("D3", ["D4", "F4", "A4"], 2), ("B2", ["D4", "F4", "G#4"], 2)], [("E2", ["B3", "D4", "E4", "G#4"], 4, "fermata")]],
     "questions": ["Tonalité réelle de l'arrangement de Por una cabeza retenu (la mineur supposé) ?"]},
    {"id": "j4", "title": "Gardel, Por una cabeza → Grieg, La mort d'Åse", "a": None, "a_label": "Gardel, Por una cabeza : fin",
     "b": ("grieg", 1, 4), "tempo_a": 112, "tempo_b": 48, "kind": "pont de 2 mesures, la majeur → si mineur, très ralenti",
     "bridge": [[("A2", ["C#4", "E4", "A4"], 2), ("D3", ["D4", "F#4", "A4"], 2)], [("F#2", ["A#3", "C#4", "E4", "F#4"], 4, "fermata")]],
     "questions": ["Le passage du tango (♩=112) à Åse (♩=48) est le plus brutal du medley : faut-il un silence complet plutôt qu'un pont ?"]},
    {"id": "j5", "title": "Grieg, La mort d'Åse → Fauré, Berceuse", "a": ("grieg", 21, 24), "b": None, "b_label": "Fauré, Berceuse : début",
     "tempo_a": 48, "tempo_b": 72, "kind": "enchaînement direct (si mineur → ré majeur, relatif)", "bridge": [],
     "questions": ["Enchaîner sans pont sur la respiration de Nina, ou tenir l'accord de si mineur en point d'orgue ?"]},
    {"id": "j6", "title": "Fauré, Berceuse → Massenet, Méditation", "a": None, "a_label": "Fauré, Berceuse : fin (ré majeur)", "b": ("massenet", 1, 4),
     "tempo_a": 72, "tempo_b": 66, "kind": "enchaînement direct (ré majeur → ré majeur)", "bridge": [],
     "questions": ["Deux pièces lentes en ré majeur avec Nina soliste : garder les deux, ou couper la Berceuse plus tôt ?"]},
    {"id": "j7", "title": "Massenet, Méditation → Ravel, Pavane", "a": ("massenet", 69, 72), "b": None, "b_label": "Ravel, Pavane : début",
     "tempo_a": 66, "tempo_b": 54, "kind": "pont de 2 mesures, ré majeur → sol majeur",
     "bridge": [[("D3", ["D4", "F#4", "A4"], 2), ("D3", ["C4", "F#4", "A4"], 2)], [("D3", ["C4", "F#4", "A4", "D5"], 4, "fermata")]],
     "questions": ["Nina quitte le rôle de soliste ici : qui donne la levée de la Pavane (cor solo) ?"]},
    {"id": "j8", "title": "Ravel, Pavane → Abreu, Tico-Tico", "a": None, "a_label": "Ravel, Pavane : fin d'extrait (sol majeur)", "b": None, "b_label": "Tico-Tico : début",
     "tempo_a": 54, "tempo_b": 126, "kind": "pont de 2 mesures, sol majeur → la mineur, accelerando",
     "bridge": [[("G2", ["B3", "D4", "G4"], 2), ("G#2", ["B3", "D4", "E4"], 2)], [("E2", ["B3", "D4", "E4", "G#4"], 4, "accel")]],
     "questions": ["Accelerando écrit sur mi⁷ (deux mesures) ou coupure nette et départ de la percussion ?", "Tonalité de l'arrangement de Tico-Tico retenu (la mineur ou si♭ majeur selon les versions trouvées) ?"]},
]


def load(key):
    return m21.converter.parse(str(SRC / SOURCES[key]["file"]), quantizePost=True)


_cache = {}


def excerpt(key, a, b):
    """Réduction piano (chordify) des mesures a–b, répartie main droite / main gauche autour du do3 (C4)."""
    if key not in _cache:
        _cache[key] = load(key).chordify()
    ch = _cache[key]
    rh_measures, lh_measures = [], []
    for m in ch.getElementsByClass(m21.stream.Measure):
        if not (a <= m.number <= b):
            continue
        rh, lh = m21.stream.Measure(), m21.stream.Measure()
        for el in m.notesAndRests:
            ql = el.quarterLength
            if el.isRest or ql == 0:
                rh.insert(el.offset, m21.note.Rest(quarterLength=ql)); lh.insert(el.offset, m21.note.Rest(quarterLength=ql)); continue
            hi = [p for p in el.pitches if p.ps >= 60]
            lo = [p for p in el.pitches if p.ps < 60]
            rh.insert(el.offset, m21.chord.Chord(hi, quarterLength=ql) if hi else m21.note.Rest(quarterLength=ql))
            lh.insert(el.offset, m21.chord.Chord(lo, quarterLength=ql) if lo else m21.note.Rest(quarterLength=ql))
        rh.insert(0, m21.expressions.TextExpression(f"mes. {m.number}") if m.number in (a, b) else m21.note.Rest(quarterLength=0))
        rh_measures.append(rh); lh_measures.append(lh)
    return rh_measures, lh_measures


def placeholder(label):
    rh, lh = m21.stream.Measure(), m21.stream.Measure()
    r = m21.note.Rest(quarterLength=4); r.fullMeasure = True
    rh.append(r); lh.append(m21.note.Rest(quarterLength=4))
    rh.insert(0, m21.expressions.TextExpression(f"[{label} — source à fournir]"))
    return [rh], [lh]


def bridge(spec):
    rhs, lhs = [], []
    for i, bar in enumerate(spec):
        rh, lh = m21.stream.Measure(), m21.stream.Measure()
        off = 0.0
        for ev in bar:
            bass, ups, ql, *flag = ev
            c = m21.chord.Chord(ups, quarterLength=ql)
            n = m21.note.Note(bass, quarterLength=ql)
            if flag and flag[0] == "fermata":
                c.expressions.append(m21.expressions.Fermata()); n.expressions.append(m21.expressions.Fermata())
            rh.insert(off, c); lh.insert(off, n); off += ql
            if flag and flag[0] == "accel":
                rh.insert(0, m21.expressions.TextExpression("accel."))
        if i == 0:
            rh.insert(0, m21.expressions.TextExpression("PONT (esquisse)"))
        rhs.append(rh); lhs.append(lh)
    return rhs, lhs


summary = []
for j in JONCTIONS:
    rh_all, lh_all, segments = [], [], []
    if j["a"]:
        r, l = excerpt(*j["a"]); segments.append(("A", SOURCES[j["a"][0]]["label"], f"mes. {j['a'][1]}–{j['a'][2]}", SOURCES[j["a"][0]]["reliable"]))
    else:
        r, l = placeholder(j["a_label"]); segments.append(("A", j["a_label"], "—", None))
    rh_all += r; lh_all += l
    first_bridge = len(rh_all)
    if j["bridge"]:
        r, l = bridge(j["bridge"]); rh_all += r; lh_all += l
    if j["b"]:
        r, l = excerpt(*j["b"]); segments.append(("B", SOURCES[j["b"][0]]["label"], f"mes. {j['b'][1]}–{j['b'][2]}", SOURCES[j["b"][0]]["reliable"]))
    else:
        r, l = placeholder(j["b_label"]); segments.append(("B", j["b_label"], "—", None))
    first_b = len(rh_all)
    rh_all += r; lh_all += l

    rh_part, lh_part = m21.stream.Part(), m21.stream.Part()
    rh_part.partName, lh_part.partName = "Réduction", ""
    rh_part.insert(0, m21.instrument.Piano()); lh_part.insert(0, m21.instrument.Piano())
    rh_part.insert(0, m21.clef.TrebleClef()); lh_part.insert(0, m21.clef.BassClef())
    for k, (r, l) in enumerate(zip(rh_all, lh_all), start=1):
        r.number = l.number = k
        if k == 1:
            r.insert(0, m21.meter.TimeSignature("4/4")); l.insert(0, m21.meter.TimeSignature("4/4"))
            r.insert(0, m21.tempo.MetronomeMark(number=j["tempo_a"]))
        if k == first_b + 1:
            r.insert(0, m21.tempo.MetronomeMark(number=j["tempo_b"]))
        if k == first_bridge + 1 and j["bridge"]:
            r.insert(0, m21.tempo.MetronomeMark(number=round((j["tempo_a"] + j["tempo_b"]) / 2)))
        rh_part.append(r); lh_part.append(l)
    sc = m21.stream.Score([rh_part, lh_part])
    sc.insert(0, m21.layout.StaffGroup([rh_part, lh_part], symbol="brace"))
    sc.metadata = m21.metadata.Metadata(title=f"Jonction {j['id'][1:]} : {j['title']}", composer="Medley « Nina soliste » — réduction de travail")
    xml = OUT / f"{j['id']}.musicxml"
    sc.write("musicxml", fp=str(xml))
    sc.write("midi", fp=str(OUT / f"{j['id']}.mid"))
    summary.append({"id": j["id"], "title": j["title"], "kind": j["kind"], "segments": segments, "questions": j["questions"],
                    "complete": all(s[3] for s in segments), "bridge_bars": len(j["bridge"])})
    print(xml)

(OUT / "jonctions.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
