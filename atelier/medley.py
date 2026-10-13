"""Planifier et évaluer un medley : ordre, ponts, minutage, énergie, effectif.

Plan JSON/YAML :
  target_minutes: 30
  tolerance: 2                  # minutes acceptées autour de la cible
  base_forces: [fl2, ob2, cl2, fg2, cor2, harpe, cordes]   # pour mémoire
  pieces:
    - title: Ravel, Pavane pour une infante défunte (A–B)
      key: G major              # tonalité de début de l'extrait
      end_key: G major          # tonalité de fin (défaut : key)
      tempo: 54                 # pulsations/min (noire, ou noire pointée en 6/8 et 9/8, blanche pointée pour une valse à un)
      meter: 4                  # pulsations par mesure, dans l'unité du tempo (6/8 à la noire pointée : 2 ; 9/8 : 3)
      minutes: 3.5              # durée de l'extrait
      fixed: last | first | <position 1..n>
      extra: [trompettes, percussion]   # au-delà de l'effectif de base
      verify: true              # tonalité à confirmer sur la partition

Le coût d'un ordre = somme des distances tonales (cycle des quintes) entre fin d'un extrait
et début du suivant. Les ponts sont dimensionnés par cette distance ; leur durée est calculée
au tempo de l'extrait suivant et ajoutée au total.
"""
from __future__ import annotations
import itertools, json
from pathlib import Path

CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]
ALIASES = {"Gb": "F#", "Db": "C#", "Ab": "G#", "Eb": "D#", "Bb": "A#", "Cb": "B", "Fb": "E", "E#": "F", "B#": "C",
           "E-": "D#", "B-": "A#", "A-": "G#", "D-": "C#", "G-": "F#"}
SLOW, FAST = 72, 110


def _tonic_major(key: str) -> str:
    parts = key.strip().split()
    tonic = parts[0].replace("♭", "b").replace("♯", "#")
    tonic = tonic[0].upper() + tonic[1:]
    tonic = ALIASES.get(tonic, tonic)
    mode = parts[1].lower() if len(parts) > 1 else "major"
    if mode.startswith("min"):
        return CIRCLE[(CIRCLE.index(tonic) - 3) % 12]  # relatif majeur
    return tonic


def distance(k1: str, k2: str) -> int:
    a, b = CIRCLE.index(_tonic_major(k1)), CIRCLE.index(_tonic_major(k2))
    d = abs(a - b) % 12
    return min(d, 12 - d)


def bridge_bars(d: int) -> int:
    return 0 if d == 0 else 2 if d == 1 else 4 if d <= 3 else 8


def transition(prev: dict, nxt: dict) -> dict:
    d = distance(prev.get("end_key") or prev["key"], nxt["key"])
    bars = bridge_bars(d)
    tempo = nxt.get("tempo") or 80
    minutes = bars * nxt.get("meter", 4) / tempo
    if d == 0:
        how = "enchaînement direct, même tonalité"
    elif d == 1:
        how = "pont de 2 mesures (ton voisin)"
    elif d <= 3:
        how = f"pont de 4 mesures qui module ({d} quintes)"
    else:
        how = f"pont de 8 mesures, ou coupure nette sur un accord commun ({d} quintes)"
    t1, t2 = prev.get("tempo"), nxt.get("tempo")
    if t1 and t2 and not (0.95 <= t2 / t1 <= 1.05):
        how += f" ; tempo {t1}→{t2}" + (" (point d'orgue ou ritenuto puis nouveau départ)" if abs(t2 - t1) > 30 else "")
    return {"distance": d, "bars": bars, "minutes": round(minutes, 2), "how": how}


ENERGY_WEIGHT = 3  # une fenêtre de trois extraits lents (ou rapides) « coûte » autant que 3 quintes


def key_cost(order: list[dict]) -> int:
    return sum(distance(order[i].get("end_key") or order[i]["key"], order[i + 1]["key"]) for i in range(len(order) - 1))


def energy_runs(order: list[dict]) -> int:
    """Nombre de fenêtres de trois extraits consécutifs tous lents ou tous rapides."""
    t = [p.get("tempo") for p in order]
    return sum(1 for i in range(len(t) - 2)
               if all(x and x < SLOW for x in t[i:i + 3]) or all(x and x > FAST for x in t[i:i + 3]))


def cost(order: list[dict]) -> int:
    return key_cost(order) + ENERGY_WEIGHT * energy_runs(order)


def _slots(pieces: list[dict]) -> tuple[list[dict | None], list[dict]]:
    n = len(pieces)
    slots: list[dict | None] = [None] * n
    free = []
    for p in pieces:
        f = p.get("fixed")
        pos = 0 if f == "first" else n - 1 if f == "last" else (int(f) - 1 if isinstance(f, int) or (isinstance(f, str) and f.isdigit()) else None)
        if pos is not None:
            if slots[pos] is not None:
                raise ValueError(f"deux pièces fixées à la place {pos + 1}")
            slots[pos] = p
        else:
            free.append(p)
    return slots, free


def _fill(slots, items):
    it = iter(items)
    return [s if s is not None else next(it) for s in slots]


def best_order(pieces: list[dict]) -> list[dict]:
    slots, free = _slots(pieces)
    free_idx = [i for i, s in enumerate(slots) if s is None]
    if len(free) <= 7:
        return min((_fill(slots, perm) for perm in itertools.permutations(free)), key=cost)
    # recherche locale déterministe : départs multiples + échanges 2 à 2 jusqu'à stabilité
    starts = [free, sorted(free, key=lambda p: CIRCLE.index(_tonic_major(p["key"]))),
              sorted(free, key=lambda p: p.get("tempo") or 0)]
    best = None
    for st in starts:
        order = _fill(slots, st)
        improved = True
        while improved:
            improved = False
            for a, b in itertools.combinations(free_idx, 2):
                cand = order[:]
                cand[a], cand[b] = cand[b], cand[a]
                if cost(cand) < cost(order):
                    order, improved = cand, True
        if best is None or cost(order) < cost(best):
            best = order
    return best


def evaluate(order: list[dict], spec: dict) -> dict:
    steps, bridges = [], 0.0
    for i, p in enumerate(order):
        tr = transition(p, order[i + 1]) if i + 1 < len(order) else None
        if tr:
            bridges += tr["minutes"]
        steps.append({"n": i + 1, "title": p["title"], "key": p["key"], "end_key": p.get("end_key") or p["key"],
                      "tempo": p.get("tempo"), "minutes": p.get("minutes", 0), "extra": p.get("extra", []),
                      "verify": bool(p.get("verify")), "transition_after": tr})
    music = sum(s["minutes"] for s in steps)
    total = round(music + bridges, 1)
    target, tol = spec.get("target_minutes"), spec.get("tolerance", 2)
    warnings = []
    tempi = [s["tempo"] for s in steps]
    for i in range(len(tempi) - 2):
        win = tempi[i:i + 3]
        if all(t and t < SLOW for t in win):
            warnings.append(f"trois extraits lents d'affilée ({i + 1}–{i + 3}) : risque de creux")
        if all(t and t > FAST for t in win):
            warnings.append(f"trois extraits rapides d'affilée ({i + 1}–{i + 3}) : fatigue des cordes et des vents")
    far = [s["n"] for s in steps if s["transition_after"] and s["transition_after"]["distance"] >= 4]
    if far:
        warnings.append(f"ponts longs (≥ 4 quintes) après les extraits {far} : écrire un vrai pont ou couper sur un accord commun")
    extras = sorted({e for s in steps for e in s["extra"]})
    verify = [s["title"] for s in steps if s["verify"]]
    verdict = None
    if target:
        verdict = "ok" if abs(total - target) <= tol else ("trop long" if total > target else "trop court")
    return {"name": spec.get("name"), "order": steps, "music_minutes": round(music, 1), "bridge_minutes": round(bridges, 1),
            "total_minutes": total, "target_minutes": target, "verdict": verdict, "key_cost": key_cost(order),
            "energy_runs": energy_runs(order),
            "warnings": warnings, "extra_forces": extras, "to_verify": verify}


def plan(spec: dict) -> dict:
    return evaluate(best_order(spec["pieces"]), spec)


def _read(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if str(path).endswith((".yaml", ".yml")):
        import yaml  # type: ignore
        return yaml.safe_load(text)
    return json.loads(text)


def load_spec(path: str | Path) -> dict:
    """Charge un plan ; une pièce `{"ref": "id", ...}` est complétée depuis le fichier `repertoire`."""
    path = Path(path)
    spec = _read(path)
    if spec.get("repertoire"):
        rep = _read((path.parent / spec["repertoire"]).resolve())
        by_id = {p["id"]: p for p in rep["pieces"]}
        pieces = []
        for p in spec["pieces"]:
            if "ref" in p:
                if p["ref"] not in by_id:
                    raise SystemExit(f"référence inconnue dans le répertoire : {p['ref']}")
                base = {k: v for k, v in by_id[p["ref"]].items() if k not in ("id", "notes")}
                base.update({k: v for k, v in p.items() if k != "ref"})
                p = base
            pieces.append(p)
        spec["pieces"] = pieces
    return spec


def to_markdown(res: dict) -> str:
    lines = [f"| # | Extrait | Ton. | Tempo | Min | Puis |", "|---|---|---|---|---|---|"]
    for s in res["order"]:
        tr = s["transition_after"]
        k = s["key"] if s["key"] == s["end_key"] else f"{s['key']} → {s['end_key']}"
        lines.append(f"| {s['n']} | {s['title']}{' ⚠' if s['verify'] else ''} | {k} | {s['tempo'] or ''} | {s['minutes']} | {tr['how'] if tr else 'fin'} |")
    lines.append("")
    lines.append(f"**Musique {res['music_minutes']} min + ponts {res['bridge_minutes']} min = {res['total_minutes']} min** "
                 f"(cible {res['target_minutes']}) : **{res['verdict']}** ; coût tonal {res['key_cost']}.")
    if res["extra_forces"]:
        lines.append(f"Effectif en plus de la base : {', '.join(res['extra_forces'])}.")
    for w in res["warnings"]:
        lines.append(f"- {w}")
    return "\n".join(lines)


def main(args) -> int:
    res = plan(load_spec(args.plan))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    elif getattr(args, "markdown", False):
        print(to_markdown(res))
    else:
        for s in res["order"]:
            print(f"{s['n']:2d}. {s['title']}  [{s['key']}, ♩={s['tempo']}, {s['minutes']} min]{'  (tonalité à vérifier)' if s['verify'] else ''}")
            if s["transition_after"]:
                print(f"      → {s['transition_after']['how']} [{s['transition_after']['minutes']} min]")
        print(f"Musique {res['music_minutes']} + ponts {res['bridge_minutes']} = {res['total_minutes']} min (cible {res['target_minutes']}) : {res['verdict']} ; coût tonal {res['key_cost']}")
        for w in res["warnings"]:
            print("  !", w)
        if res["extra_forces"]:
            print("  effectif en plus :", ", ".join(res["extra_forces"]))
    return 0 if res["verdict"] in (None, "ok") else 2
