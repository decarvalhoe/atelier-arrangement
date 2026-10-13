"""Accord sur le dernier temps de chaque mesure (réduction chordify) : repérer les cadences.
Usage : python tools/bar_chords.py fichier [debut fin]"""
import sys
import music21 as m21

s = m21.converter.parse(sys.argv[1], quantizePost=sys.argv[1].lower().endswith(".mid"))
a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
b = int(sys.argv[3]) if len(sys.argv) > 3 else 10_000
ch = s.chordify()
for m in ch.getElementsByClass(m21.stream.Measure):
    if not (a <= m.number <= b):
        continue
    chords = [c for c in m.recurse().getElementsByClass(m21.chord.Chord)]
    if not chords:
        print(f"{m.number:4d}  —")
        continue
    last = chords[-1]
    names = sorted({p.name for p in last.pitches})
    print(f"{m.number:4d}  {last.pitchedCommonName:28s} basse {last.bass().name:3s} {names}")
