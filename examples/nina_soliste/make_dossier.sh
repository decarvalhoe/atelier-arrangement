#!/bin/sh
# Rend les jonctions : PDF par MuseScore (mode sans écran), WAV par FluidSynth (MS Basic), puis enchaînement audio.
# Usage : sh examples/nina_soliste/make_dossier.sh   (depuis la racine du dépôt, après tools/setup-wsl-userspace.sh)
set -eu
export PATH="$HOME/.local/bin:$PATH"
PY="$HOME/.local/atelier/env/bin/python"
SRC=work/nina/src
OUT=work/nina/dossier
SF=work/soundfonts/ms-basic.sf3
mkdir -p "$OUT/pdf" "$OUT/audio"
"$PY" -W ignore examples/nina_soliste/build_jonctions.py "$SRC" "$OUT/xml"
for x in "$OUT"/xml/j*.musicxml; do
  b=$(basename "$x" .musicxml)
  mscore -o "$OUT/pdf/$b.pdf" "$x" >/dev/null 2>&1 || echo "MuseScore : échec sur $b"
  fluidsynth -ni -q -g 0.8 -r 44100 -F "$OUT/audio/$b.wav" "$SF" "$OUT/xml/$b.mid" >/dev/null 2>&1 || echo "FluidSynth : échec sur $b"
done
# une seule piste d'écoute : jonctions séparées par 2 s de silence, en MP3
ffmpeg -loglevel error -y -f lavfi -t 2 -i anullsrc=r=44100:cl=stereo "$OUT/audio/_silence.wav"
: > "$OUT/audio/_liste.txt"
for w in "$OUT"/audio/j*.wav; do echo "file '$(basename "$w")'" >> "$OUT/audio/_liste.txt"; echo "file '_silence.wav'" >> "$OUT/audio/_liste.txt"; done
(cd "$OUT/audio" && ffmpeg -loglevel error -y -f concat -safe 0 -i _liste.txt -codec:a libmp3lame -q:a 3 jonctions-nina-soliste.mp3)
"$PY" -m atelier dossier "$OUT"/pdf/j*.pdf --out "$OUT/jonctions-reduction.pdf" --title "Medley Nina soliste — jonctions (réduction de travail)"
ls -la "$OUT/pdf" "$OUT/audio" "$OUT/jonctions-reduction.pdf"
