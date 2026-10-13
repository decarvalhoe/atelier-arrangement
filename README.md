# Atelier d'arrangement

Une seule ligne de commande pour tirer le maximum de la chaîne libre d'arrangement : **MuseScore Studio**, **LilyPond**, **Audiveris**, **music21**, **Verovio**, **FluidSynth** (+ VSCO 2 CE), **PyMuPDF / pdfcpu / qpdf**, **Git**. Objectif : écrire des arrangements de niveau professionnel, produire du matériel d'orchestre conforme aux usages (MOLA), et assembler des medleys d'une demi-heure pour orchestre réduit, le tout scriptable et pilotable par des agents de code.

## Installation

```bash
# Windows
pwsh tools/setup-windows.ps1
# Debian / Ubuntu / WSL
sh tools/setup-linux.sh
```

Puis `python -m atelier env` dit ce qui manque. Audiveris et la banque VSCO 2 CE (CC0) se téléchargent à la main (liens affichés par le script) ; un chemin non standard se déclare par variable d'environnement, par exemple `ATELIER_AUDIVERIS=C:\Outils\Audiveris\Audiveris.exe`.

## La chaîne en sept commandes

```bash
python -m atelier medley examples/medley-demi-heure.json            # 1. ordre, transitions, minutage
python -m atelier render audiveris work/sources/scan.pdf --out work/omr   # 2. OMR si aucun encodage n'existe
python -m atelier analyse work/omr/piece.musicxml                   # 3. mesures, tonalités, tessitures
python -m atelier extract work/omr/piece.musicxml 16 27 --parts violon alto --transpose 2   # 4. couper, transposer
python -m atelier check work/arrangement.musicxml --require-marks 33 71   # 5. contrôles (mesures, tessitures, repères, cues)
python -m atelier render musescore work/arrangement.mscz --out work/out/arr.pdf --parts   # 6. conducteur + parties
python -m atelier dossier work/out/*.pdf --out work/out/dossier.pdf --title "Matériel"     # 7. dossier musiciens
```

`make env test medley analyse check parts audio dossier` enchaîne les mêmes étapes avec des variables (`SRC`, `PLAN`, `SF2`).

## Ce que font les commandes

| Commande | Rôle |
|---|---|
| `env` | localise chaque outil (PATH, emplacements usuels, variables `ATELIER_*`) et les modules Python |
| `analyse` | structure (mesures, chiffrages, tempi, repères), tonalité par fenêtre de 8 mesures, tessiture et notes hors limite par partie |
| `extract` | mesures a–b, parties choisies, transposition → MusicXML prêt pour MuseScore ou LilyPond |
| `engrave` | MusicXML/MEI/ABC → SVG (Verovio) pour fiches, programmes, documents de travail |
| `render` | MuseScore en batch (PDF, MusicXML, MIDI, parties), LilyPond, Audiveris en batch, FluidSynth |
| `check` | erreurs bloquantes : mesures incohérentes entre parties, notes hors limite, repère manquant à une jonction ; avertissements : hors confort, cues à prévoir après un long silence, absence de repères |
| `medley` | ordre optimal par proximité sur le cycle des quintes (pièces fixées en tête ou en fin), transition conseillée entre chaque pièce, total contre la cible |
| `dossier` | fusion de PDF, page de titre, numérotation |

Les tessitures et transpositions sont dans `atelier/ranges.py` (notes écrites, bornes « confort » et « limite » pour un orchestre d'étudiants) : à ajuster à l'orchestre réel.

## Travailler avec un agent de code

`AGENTS.md` (importé par `CLAUDE.md`) donne les règles et les commandes. Un agent peut, par exemple : « Prépare le programme 1 du fichier `examples/medley-demi-heure.json` : trouve les encodages, analyse chaque pièce, propose les ponts, extrais les passages, vérifie les tessitures pour l'effectif 2.2.2.2–2.0.0.0–cordes, et produis un rapport. » Les choix d'orchestration restent humains ; l'agent fournit les chiffres et exécute.

## Intégration continue

`.github/workflows/ci.yml` installe LilyPond, lance les tests, le plan de medley et compile l'exemple `examples/pont.ly` ; le PDF produit est un artefact du run. Le même fichier sert de modèle pour régénérer un matériel complet à chaque commit (ajouter `render musescore` avec une AppImage MuseScore).

## Structure

```
atelier/        paquet Python (env, analyse, extract, engrave, render, check, medley, dossier, ranges)
tests/          tests pytest (partition générée, contrôles, extraction, gravure, plan)
tools/          scripts d'installation Windows et Linux
examples/       plan de medley JSON, pont LilyPond
docs/outils.md  matrice des outils et licences
work/           sources, OMR, sorties (ignoré par Git)
```

## Licence

Code : MIT. Les partitions que vous produisez vous appartiennent ; publiez vos arrangements d'œuvres du domaine public sous licence libre (CC BY ou CC BY-SA) sur IMSLP ou Mutopia.
