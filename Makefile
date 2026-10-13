# Chaîne complète d'un projet d'arrangement. Variables à surcharger : SRC (mscz/ly), PLAN (medley), SF2 (banque).
PY ?= python
SRC ?= work/arrangement.mscz
PLAN ?= examples/medley-demi-heure.json
SF2 ?= work/soundfonts/vsco2.sf2
OUT ?= work/out

.PHONY: env test analyse check parts audio dossier medley clean

env:            ## état des outils
	$(PY) -m atelier env

test:           ## tests unitaires
	$(PY) -m pytest -q

medley:         ## ordre, transitions, minutage
	$(PY) -m atelier medley $(PLAN)

analyse:        ## structure, tonalités, tessitures de SRC (MusicXML)
	$(PY) -m atelier analyse $(SRC)

check:          ## contrôles du matériel (échoue sur erreur)
	$(PY) -m atelier check $(SRC)

parts:          ## conducteur + parties PDF via MuseScore (ou LilyPond si SRC est un .ly)
	mkdir -p $(OUT)
ifeq ($(suffix $(SRC)),.ly)
	$(PY) -m atelier render lilypond $(SRC) --out $(OUT)
else
	$(PY) -m atelier render musescore $(SRC) --out $(OUT)/$(basename $(notdir $(SRC))).pdf --parts
endif

audio:          ## maquette audio (MIDI exporté par MuseScore + FluidSynth)
	$(PY) -m atelier render musescore $(SRC) --out $(OUT)/maquette.mid
	$(PY) -m atelier render fluidsynth $(OUT)/maquette.mid --soundfont $(SF2) --out $(OUT)/maquette.wav

dossier:        ## toutes les parties PDF en un dossier numéroté
	$(PY) -m atelier dossier $(OUT)/*.pdf --out $(OUT)/dossier-musiciens.pdf --title "Matériel d'orchestre"

clean:
	rm -rf $(OUT)
