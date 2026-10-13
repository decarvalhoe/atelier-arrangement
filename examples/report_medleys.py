"""Compte rendu des medleys de démonstration -> docs/medleys-testes.md (français).
Usage : python examples/report_medleys.py [sortie.md]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from atelier import medley  # noqa: E402

NOTES = {"C": "do", "D": "ré", "E": "mi", "F": "fa", "G": "sol", "A": "la", "B": "si"}


def fr_key(k: str) -> str:
    t, *mode = k.split()
    name = NOTES[t[0].upper()] + {"#": "♯", "-": "♭", "b": "♭"}.get(t[1:2], "")
    return f"{name} {'mineur' if mode and mode[0].startswith('min') else 'majeur'}"


def fr_how(how: str) -> str:
    return how.replace("quintes", "quintes").replace("min", "min")


HERE = Path(__file__).parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "docs" / "medleys-testes.md"
plans = sorted((HERE / "medleys").glob("*.json"))
rows, sections = [], []
for f in plans:
    res = medley.plan(medley.load_spec(f))
    rows.append(f"| {res['name']} | {len(res['order'])} | {res['music_minutes']} + {res['bridge_minutes']} = **{res['total_minutes']}** | "
                f"{res['key_cost']} | {res['energy_runs']} | {', '.join(res['extra_forces']) or '—'} |")
    lines = [f"### {res['name']}", "", "| # | Extrait | Tonalité | Tempo | Min | Enchaînement |", "|---|---|---|---|---|---|"]
    for s in res["order"]:
        k = fr_key(s["key"]) + ("" if s["key"] == s["end_key"] else f" → {fr_key(s['end_key'])}")
        tr = s["transition_after"]
        lines.append(f"| {s['n']} | {s['title']}{' (tonalité à vérifier)' if s['verify'] else ''} | {k} | {s['tempo']} | {s['minutes']} | {tr['how'] if tr else 'fin'} |")
    lines.append("")
    lines.append(f"Musique {res['music_minutes']} min + ponts {res['bridge_minutes']} min = **{res['total_minutes']} min** ; coût tonal {res['key_cost']} ; creux d’énergie {res['energy_runs']}.")
    for w in res["warnings"]:
        lines.append(f"- ⚠ {w}")
    sections.append("\n".join(lines))

md = f"""## Tests en mode medley

Le medley enchaîne des **extraits** sans pause, reliés par des ponts. Chaque essai ci-dessous a été calculé par l’outil `atelier medley` ([dépôt atelier-arrangement](https://github.com/decarvalhoe/atelier-arrangement)) à partir d’un répertoire élargi de {len(medley._read(HERE / 'repertoire.json')['pieces'])} pièces (domaine public, sans baroque, orchestre réduit). L’outil :

- choisit l’ordre qui minimise les distances tonales entre la fin d’un extrait et le début du suivant (cycle des quintes), en gardant la Pavane de Ravel et *Tico-Tico* (toujours en finale) ;
- pénalise trois extraits lents (ou rapides) d’affilée ;
- dimensionne chaque pont (0, 2, 4 ou 8 mesures selon la distance tonale), le minute au tempo de l’extrait suivant et l’ajoute au total ;
- signale les instruments à ajouter à l’effectif de base et les tonalités à vérifier sur la partition.

Cible : 30 minutes ± 1,5, ponts compris.

| Medley | Extraits | Musique + ponts = total (min) | Coût tonal | Creux | Effectif en plus |
|---|---|---|---|---|---|
{chr(10).join(rows)}

**Ce que montrent les tests**

- Les sept medleys tiennent dans la demi-heure ; les ponts représentent de 0,3 à 1,1 min.
- **Le Programme 1, converti tel quel, ne marche pas bien en medley** : avec une seule pièce rapide (*Tico-Tico*), trois extraits lents restent enchaînés quel que soit l’ordre. Remplacer l’Entr’acte de *Carmen* par l’Aragonaise et ajouter le Menuet de Boccherini (variante 1b) supprime le creux et fait passer le coût tonal de 13 à 9.
- **« Effectif de base seul »** est le seul medley qui ne demande rien de plus que bois par deux, deux cors, harpe et cordes (plus une percussion légère pour *Tico-Tico*) : c’est le plus simple à monter.
- **« Nina soliste »** a les meilleurs enchaînements (coût tonal 6) : presque tout se fait par ton voisin.
- **« Paris 1900 »** a la plus belle couleur mais un passage tonal lointain (Clair de lune en ré♭ majeur) : il faut y écrire un vrai pont ou couper sur un accord commun.
- **« Contes et ballets »** est le plus spectaculaire, mais le plus exigeant en effectif (trompettes, trombones, timbales, percussion, célesta ou piano).
- Les tonalités marquées « à vérifier » (*Tico-Tico*, *Por una cabeza*, Gymnopédie, Pizzicato-Polka) dépendent de l’édition ou de l’arrangement retenu : les confirmer avant d’écrire les ponts.

{chr(10).join(sections)}
"""
out.write_text(md, encoding="utf-8")
print(out)
