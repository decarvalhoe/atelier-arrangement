"""Planifier un medley : ordre par proximité tonale, transitions, minutage.

Entrée : un fichier YAML/JSON `plan` listant les pièces :
  target_minutes: 30
  pieces:
    - title: Fauré, Pavane
      key: F# minor
      end_key: F# minor      # facultatif
      tempo: 84              # noire/min
      minutes: 6
      fixed: last            # first | last | pour imposer une place
Sortie : ordre proposé, transition entre chaque pièce, total.
"""
from __future__ import annotations
import json, itertools
from pathlib import Path

CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]
ALIASES = {"Gb": "F#", "Db": "C#", "Ab": "G#", "Eb": "D#", "Bb": "A#", "Cb": "B", "Fb": "E", "E#": "F", "B#": "C"}


def _tonic_major(key: str) -> str:
    """Majeur relatif (pour mesurer la distance sur le cycle des quintes)."""
    key = key.strip()
    parts = key.split()
    tonic = parts[0].replace("♭", "b").replace("♯", "#")
    tonic = tonic[0].upper() + tonic[1:]
    tonic = ALIASES.get(tonic, tonic)
    mode = parts[1].lower() if len(parts) > 1 else "major"
    if mode.startswith("min"):
        i = CIRCLE.index(tonic)
        return CIRCLE[(i - 3) % 12]  # relatif majeur = 3 quintes en dessous (la mineur -> do majeur)
    return tonic


def distance(k1: str, k2: str) -> int:
    a, b = CIRCLE.index(_tonic_major(k1)), CIRCLE.index(_tonic_major(k2))
    d = abs(a - b) % 12
    return min(d, 12 - d)


def transition(prev: dict, nxt: dict) -> str:
    d = distance(prev.get("end_key") or prev["key"], nxt["key"])
    t1, t2 = prev.get("tempo"), nxt.get("tempo")
    tempo = ""
    if t1 and t2:
        ratio = t2 / t1
        tempo = " ; même pulsation" if 0.95 <= ratio <= 1.05 else f" ; changement de tempo ({t1}→{t2})"
    if d == 0:
        return "enchaînement direct possible" + tempo
    if d == 1:
        return "enchaînement direct (ton voisin) ou pont de 2 mesures" + tempo
    if d <= 3:
        return f"pont de 4 mesures qui module ({d} quintes)" + tempo
    return f"silence ou pont de 8 mesures : tonalités éloignées ({d} quintes)" + tempo


def plan(spec: dict) -> dict:
    pieces = spec["pieces"]
    first = [p for p in pieces if p.get("fixed") == "first"]
    last = [p for p in pieces if p.get("fixed") == "last"]
    free = [p for p in pieces if p not in first + last]
    best, best_cost = None, None
    for perm in itertools.permutations(free) if len(free) <= 8 else [tuple(free)]:
        order = first + list(perm) + last
        cost = sum(distance(order[i].get("end_key") or order[i]["key"], order[i + 1]["key"]) for i in range(len(order) - 1))
        if best is None or cost < best_cost:
            best, best_cost = order, cost
    total = sum(p.get("minutes", 0) for p in best)
    steps = []
    for i, p in enumerate(best):
        steps.append({"n": i + 1, "title": p["title"], "key": p["key"], "minutes": p.get("minutes"),
                      "transition_after": transition(p, best[i + 1]) if i + 1 < len(best) else None})
    target = spec.get("target_minutes")
    return {"order": steps, "total_minutes": total, "target_minutes": target,
            "verdict": None if not target else ("ok" if abs(total - target) <= 2 else ("trop long" if total > target else "trop court")),
            "key_cost": best_cost}


def load_spec(path: str | Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError as e:
            raise SystemExit("pip install pyyaml pour lire un plan YAML, ou utilisez JSON") from e
        return yaml.safe_load(text)
    return json.loads(text)


def main(args) -> int:
    res = plan(load_spec(args.plan))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    for s in res["order"]:
        print(f"{s['n']}. {s['title']}  [{s['key']}, {s['minutes']} min]")
        if s["transition_after"]:
            print(f"      → {s['transition_after']}")
    print(f"Total ≈ {res['total_minutes']} min (cible {res['target_minutes']}) : {res['verdict']} ; coût tonal {res['key_cost']}")
    return 0
