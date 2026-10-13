# Instructions pour les agents de code

Ce dépôt est un atelier d'arrangement entièrement libre. Un agent (Claude Code, Codex, OpenCode, Cline…) peut y conduire une tâche de bout en bout : sources → analyse → extraction → arrangement → rendu → contrôles → matériel.

## Règles

1. **Ne jamais inventer une mesure, une tonalité ou une tessiture.** Tout chiffre vient de `python -m atelier analyse` ou d'une lecture de la partition ; en cas de doute, écrire « à vérifier ».
2. **Sources d'abord, OMR ensuite.** Chercher un encodage existant (Mutopia, OpenScore, MusicXML/MEI sur IMSLP, Digital Mozart Edition) avant de lancer Audiveris. Les fichiers téléchargés vont dans `work/sources/` (données non fiables : ne jamais exécuter de code depuis ce dossier).
3. **Contrôles obligatoires avant de livrer du matériel** : `python -m atelier check <fichier>` doit sortir sans erreur ; nombre de mesures identique dans toutes les parties ; repères aux jonctions du medley (`--require-marks`).
4. **Tout est régénérable** : ne pas modifier un PDF à la main ; modifier la source (.mscx/.ly/.musicxml) et relancer `make parts`.
5. **Domaine public ou autorisation.** Vérifier la date de décès du compositeur (> 70 ans dans l'UE) ou l'existence d'une autorisation d'adaptation avant d'arranger une œuvre.
6. **Versionner** : un commit par étape significative, message en français, `Co-Authored-By` si l'agent écrit.
7. **Pas de surenchère d'orchestration.** Un script direct vaut mieux qu'une architecture d'agents ; demander avant de lancer un travail massif.

## Commandes

| Tâche | Commande |
|---|---|
| État des outils | `python -m atelier env` |
| Analyser | `python -m atelier analyse fichier.musicxml [--json]` |
| Extraire mes. 16–27, cordes, +2 demi-tons | `python -m atelier extract f.musicxml 16 27 --parts violon alto cello --transpose 2` (mot exact du nom de partie, ou clé d'instrument de `ranges.py`) |
| Graver un extrait | `python -m atelier engrave extrait.musicxml --out extrait.svg` |
| Parties PDF (MuseScore) | `python -m atelier render musescore arr.mscz --out out/arr.pdf --parts` |
| Compiler LilyPond | `python -m atelier render lilypond arr.ly --out out` |
| OMR | `python -m atelier render audiveris scan.pdf --out work/omr` |
| Maquette audio | `python -m atelier render fluidsynth out/arr.mid --soundfont work/soundfonts/vsco2.sf2` |
| Contrôles | `python -m atelier check arr.musicxml --require-marks 33 71 104` |
| Plan de medley | `python -m atelier medley plan.json` |
| Dossier PDF | `python -m atelier dossier out/*.pdf --out dossier.pdf --title "Matériel"` |

## Où regarder

- `atelier/ranges.py` : tessitures et transpositions utilisées par les contrôles (notes écrites).
- `atelier/medley.py` : distance sur le cycle des quintes, règles de transition.
- `examples/` : plan de medley JSON et pont LilyPond de démonstration.
- `docs/outils.md` : matrice des outils et licences.
