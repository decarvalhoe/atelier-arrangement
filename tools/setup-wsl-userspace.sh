#!/bin/sh
# Installe toute la chaîne SANS sudo, dans ~/.local (WSL ou Linux sans droits administrateur).
# Sources officielles uniquement : micromamba (conda-forge), LilyPond (gitlab.com/lilypond),
# MuseScore Studio (AppImage GitHub, extraite : pas besoin de FUSE), pdfcpu (GitHub).
# Idempotent : relancer après une coupure réseau.
set -eu
PREFIX="$HOME/.local/atelier"
BIN="$HOME/.local/bin"
ENV="$PREFIX/env"
DL="$PREFIX/downloads"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LILY_VER=2.24.4
MS_URL=https://github.com/musescore/MuseScore/releases/download/v4.7.5/MuseScore-Studio-4.7.5.260831071-x86_64.AppImage
PDFCPU_URL=https://github.com/pdfcpu/pdfcpu/releases/download/v0.16.2/pdfcpu_0.16.2_Linux_x86_64.tar.xz
mkdir -p "$PREFIX" "$BIN" "$DL"

echo "== micromamba"
if [ ! -x "$BIN/micromamba" ]; then
  curl -fsSL https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C "$PREFIX" bin/micromamba
  ln -sf "$PREFIX/bin/micromamba" "$BIN/micromamba"
fi

echo "== environnement conda-forge : Python 3.12, FluidSynth, qpdf, libsndfile"
if [ ! -x "$ENV/bin/python" ]; then
  "$BIN/micromamba" create -y -q -p "$ENV" -c conda-forge python=3.12 fluidsynth qpdf libsndfile
fi
ln -sf "$ENV/bin/fluidsynth" "$BIN/fluidsynth"
ln -sf "$ENV/bin/qpdf" "$BIN/qpdf"

echo "== LilyPond $LILY_VER"
if [ ! -x "$PREFIX/lilypond-$LILY_VER/bin/lilypond" ]; then
  curl -fsSL -o "$DL/lilypond.tgz" "https://gitlab.com/lilypond/lilypond/-/releases/v$LILY_VER/downloads/lilypond-$LILY_VER-linux-x86_64.tar.gz"
  tar -xzf "$DL/lilypond.tgz" -C "$PREFIX"
fi
for t in lilypond musicxml2ly midi2ly convert-ly; do ln -sf "$PREFIX/lilypond-$LILY_VER/bin/$t" "$BIN/$t"; done

echo "== MuseScore Studio (AppImage extraite)"
if [ ! -x "$PREFIX/musescore/AppRun" ]; then
  curl -fsSL -o "$DL/musescore.AppImage" "$MS_URL"
  chmod +x "$DL/musescore.AppImage"
  (cd "$PREFIX" && "$DL/musescore.AppImage" --appimage-extract >/dev/null && rm -rf musescore && mv squashfs-root musescore)
fi
cat > "$BIN/mscore" <<'EOF'
#!/bin/sh
# MuseScore en mode sans écran (exports en ligne de commande)
export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen}
exec "$HOME/.local/atelier/musescore/AppRun" "$@"
EOF
chmod +x "$BIN/mscore"

echo "== pdfcpu"
if [ ! -x "$BIN/pdfcpu" ]; then
  curl -fsSL -o "$DL/pdfcpu.tar.xz" "$PDFCPU_URL"
  tar -xJf "$DL/pdfcpu.tar.xz" -C "$DL"
  cp "$(find "$DL" -name pdfcpu -type f -perm -u+x | head -1)" "$BIN/pdfcpu"
fi

echo "== banque de sons : MS Basic (MIT), fournie avec MuseScore"
SF=$(find "$PREFIX/musescore" -iname 'MS Basic.sf3' -o -iname 'MS_Basic.sf3' 2>/dev/null | head -1 || true)
mkdir -p "$REPO/work/soundfonts"
[ -n "$SF" ] && ln -sf "$SF" "$REPO/work/soundfonts/ms-basic.sf3" && echo "   $SF"

echo "== paquet atelier"
"$ENV/bin/python" -m pip install -q -U pip
"$ENV/bin/python" -m pip install -q -e "$REPO[dev]"
ln -sf "$ENV/bin/atelier" "$BIN/atelier"

case ":$PATH:" in *":$BIN:"*) ;; *) echo "Ajouter à ~/.profile : export PATH=\"\$HOME/.local/bin:\$PATH\"";; esac
PATH="$BIN:$PATH" "$ENV/bin/python" -m atelier env || true
