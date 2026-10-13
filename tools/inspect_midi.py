"""Résumé rapide de fichiers MIDI : pistes, durée, mesures, tonalité estimée début/fin.
Usage : python tools/inspect_midi.py fichier.mid [...]"""
import sys
import mido
import music21 as m21

for f in sys.argv[1:]:
    try:
        mf = mido.MidiFile(f)
        names = [next((m.name for m in t if m.type == "track_name"), "") for t in mf.tracks]
        tempos = sorted({round(mido.tempo2bpm(m.tempo)) for t in mf.tracks for m in t if m.type == "set_tempo"})[:6]
        s = m21.converter.parse(f, quantizePost=True)
        ms = s.parts[0].getElementsByClass(m21.stream.Measure) if s.parts else []
        n = len(ms)
        ts = [t.ratioString for t in s.flatten().getElementsByClass(m21.meter.TimeSignature)][:3]
        def k(a, b):
            try:
                kk = s.measures(a, b).analyze("key"); return f"{kk.tonic.name} {kk.mode} ({kk.correlationCoefficient:.2f})"
            except Exception:
                return "?"
        print(f"== {f}\n   durée {mf.length:6.1f} s ; pistes {len(mf.tracks)} {[x for x in names if x][:10]} ; tempi {tempos} ; mesures {n} {ts}")
        print(f"   tonalité mes. 1–8 : {k(1, min(8, n))} ; dernières 8 : {k(max(1, n - 7), n)} ; parties {len(s.parts)} {[p.partName for p in s.parts][:10]}")
    except Exception as e:  # noqa: BLE001
        print(f"== {f}: ERREUR {e}")
