import json, subprocess, sys
from pathlib import Path
import music21 as m21
import pytest
from atelier import analyse, check, extract, engrave, medley

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def score(tmp_path):
    """Petite partition de test : violon et violoncelle, 20 mesures, un repère, une note hors limite au violoncelle."""
    s = m21.stream.Score()
    for name, clef, pitch in [("Violon I", m21.clef.TrebleClef(), "A4"), ("Violoncelle", m21.clef.BassClef(), "D3")]:
        p = m21.stream.Part(); p.partName = name
        p.insert(0, clef); p.insert(0, m21.meter.TimeSignature("4/4")); p.insert(0, m21.key.Key("D"))
        for i in range(1, 21):
            mm = m21.stream.Measure(number=i)
            if i == 9:
                mm.insert(0, m21.expressions.RehearsalMark("A"))
            n = m21.note.Note("A6" if (name == "Violoncelle" and i == 15) else pitch, quarterLength=4)
            mm.append(n); p.append(mm)
        s.insert(0, p)
    f = tmp_path / "test.musicxml"
    s.write("musicxml", fp=str(f))
    return f


def test_analyse(score):
    rep = analyse.analyse(score)
    assert rep["structure"]["measures"] == 20
    assert rep["structure"]["rehearsal_marks"] == [(9, "A")]
    names = {p["part"]: p for p in rep["parts"]}
    assert names["Violon I"]["instrument"] == "violin"
    assert names["Violoncelle"]["instrument"] == "cello"
    assert names["Violoncelle"]["out_of_limit"] == 1


def test_check_detects_range_and_marks(score):
    issues = check.check(score, require_marks_at=[9, 17])
    msgs = [(i["level"], i["part"], i["measure"]) for i in issues]
    assert ("error", "Violoncelle", 15) in msgs          # A6 hors limite
    assert ("error", "*", 17) in msgs                    # repère manquant à la jonction 17
    assert ("error", "*", 9) not in msgs                 # repère présent à 9


def test_extract_and_engrave(score, tmp_path):
    out = extract.extract(score, 5, 8, parts=["violon"], transpose=2, out=tmp_path / "x.musicxml")
    s = m21.converter.parse(str(out))
    assert len(s.parts) == 1 and len(s.parts[0].getElementsByClass(m21.stream.Measure)) == 4
    assert s.parts[0].recurse().notes[0].pitch.nameWithOctave == "B4"
    svgs = engrave.engrave(out, tmp_path / "x.svg")
    assert svgs[0].exists() and "<svg" in svgs[0].read_text(encoding="utf-8")[:200]


def test_medley_plan():
    spec = {"target_minutes": 30, "pieces": [
        {"title": "Ravel, Pavane", "key": "G major", "tempo": 54, "minutes": 6.5, "fixed": "last"},
        {"title": "Fauré, Pavane", "key": "F# minor", "tempo": 84, "minutes": 6},
        {"title": "Bizet, Adagietto", "key": "F major", "tempo": 60, "minutes": 3},
        {"title": "Massenet, Méditation", "key": "D major", "tempo": 66, "minutes": 5.5},
        {"title": "Tico-Tico", "key": "A minor", "tempo": 126, "minutes": 3},
        {"title": "Elgar, Salut d'amour", "key": "E major", "tempo": 72, "minutes": 3},
    ]}
    res = medley.plan(spec)
    assert res["order"][-1]["title"] == "Ravel, Pavane"
    assert res["verdict"] in ("ok", "trop court", "trop long")
    assert medley.distance("A minor", "C major") == 0 and medley.distance("C major", "G major") == 1


MEDLEYS = sorted((ROOT / "examples" / "medleys").glob("*.json"))


@pytest.mark.parametrize("plan_file", MEDLEYS, ids=[p.stem for p in MEDLEYS])
def test_example_medleys(plan_file):
    """Chaque medley de démonstration : 30 ± 1,5 min ponts compris, Ravel et Tico-Tico présents, Tico-Tico en dernier."""
    res = medley.plan(medley.load_spec(plan_file))
    titles = [s["title"] for s in res["order"]]
    assert res["verdict"] == "ok", (res["total_minutes"], plan_file.stem)
    assert any("Ravel" in t for t in titles) and titles[-1].startswith("Abreu")
    if plan_file.stem != "1-programme-1-en-medley":   # le programme d'origine garde un creux : c'est le constat du test
        assert res["energy_runs"] == 0, res["warnings"]


def test_energy_penalty_breaks_slow_runs():
    slow = [{"title": f"lent {i}", "key": "C major", "tempo": 50, "minutes": 3} for i in range(3)]
    fast = [{"title": f"vif {i}", "key": "C major", "tempo": 130, "minutes": 3} for i in range(3)]
    res = medley.plan({"pieces": slow + fast})
    assert res["energy_runs"] == 0


def test_cli_env_runs():
    out = subprocess.run([sys.executable, "-m", "atelier", "env"], cwd=ROOT, capture_output=True, text=True)
    assert "Python" in out.stdout
