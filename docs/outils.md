# Matrice des outils libres

| Maillon | Outil | Licence | Rôle | Commande atelier |
|---|---|---|---|---|
| Écriture, parties | MuseScore Studio 4.6 | GPL v3 | Éditeur principal, export batch (`-o`, `--export-score-parts`) | `render musescore` |
| Gravure définitive | LilyPond 2.24 + Frescobaldi | GPL | Éditions reproductibles, parties par `\book` | `render lilypond` |
| Génération de LilyPond | Abjad | MIT | Partitions construites par programme | — |
| OMR | Audiveris 5 | AGPL v3 | PDF scanné → MusicXML (mode batch) | `render audiveris` |
| OMR (photos) | oemer | MIT | Reconnaissance par réseau de neurones | — |
| Pré-traitement scans | ScanTailor Advanced, Poppler (pdftoppm) | GPL | Redresser, binariser, découper | — |
| Analyse / transformation | music21 | BSD | Tonalités, tessitures, extraction, transposition | `analyse`, `extract`, `check` |
| Gravure d'extraits | Verovio | LGPL | SVG pour fiches et documents | `engrave` |
| MIDI | mido, pretty_midi, partitura | MIT / Apache | Manipulation fine | — |
| Audio → MIDI | Basic Pitch, MT3, Demucs | Apache / MIT | Base à corriger quand seule une captation existe | — |
| Synthèse | FluidSynth + VSCO 2 Community Edition (CC0), Sonatina (CC Sampling+), sfizz (BSD) | LGPL / CC0 | Maquette audio | `render fluidsynth` |
| Séquenceur | Ardour, Qtractor, LMMS, Zrythm | GPL / AGPL | Tempo map, mixage | — |
| PDF | PyMuPDF (AGPL), pdfcpu (Apache), qpdf (Apache) | — | Fusion, imposition, numérotation | `dossier` |
| Polices | Bravura, Leland, Emmentaler (OFL) | OFL | Gravure SMuFL | — |
| Versions, CI | Git, GitHub/Forgejo Actions | GPL / — | Régénération automatique à chaque commit | `.github/workflows/ci.yml` |

Références : MOLA, *Guidelines for Music Preparation* (mola-inc.org) pour le matériel ; rapport « Outils libres d'arrangement et de medley » (octobre 2026) pour le détail et les sources.
