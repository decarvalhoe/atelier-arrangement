#!/bin/sh
# Installe la chaîne libre sur Debian/Ubuntu (WSL compris) et l'environnement Python.
set -e
sudo apt-get update
sudo apt-get install -y lilypond fluidsynth qpdf ffmpeg git python3-venv default-jre-headless
# MuseScore Studio : l'AppImage officielle est plus récente que le paquet apt
mkdir -p "$HOME/.local/bin"
if ! command -v mscore >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/mscore" ]; then
  echo "MuseScore : télécharger l'AppImage depuis https://musescore.org/fr/download, la rendre exécutable et la lier :"
  echo "  chmod +x MuseScore-Studio-*.AppImage && ln -s \$PWD/MuseScore-Studio-*.AppImage \$HOME/.local/bin/mscore"
fi
echo "Audiveris : https://github.com/Audiveris/audiveris/releases (archive Linux, Java 21+) ; exporter ATELIER_AUDIVERIS=/chemin/Audiveris"
echo "pdfcpu : https://github.com/pdfcpu/pdfcpu/releases (binaire unique) -> \$HOME/.local/bin"
echo "VSCO 2 Community Edition (CC0, .sf2) : https://vis.versilstudios.com/vsco-community.html -> work/soundfonts/"
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
python -m atelier env
