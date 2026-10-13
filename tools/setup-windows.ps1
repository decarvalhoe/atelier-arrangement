# Installe la chaîne libre sur Windows (winget) et l'environnement Python.
# Usage : pwsh tools/setup-windows.ps1   (relancer après un échec réseau : tout est idempotent)
$ErrorActionPreference = "Continue"
$pkgs = @(
  @{ id = "Musescore.Musescore"; name = "MuseScore Studio" },
  @{ id = "LilyPond.LilyPond";   name = "LilyPond (inclut musicxml2ly)" },
  @{ id = "FluidSynth.FluidSynth"; name = "FluidSynth" },
  @{ id = "QPDF.QPDF";           name = "qpdf" },
  @{ id = "pdfcpu.pdfcpu";       name = "pdfcpu" },
  @{ id = "Gyan.FFmpeg";         name = "ffmpeg" },
  @{ id = "Git.Git";             name = "git" }
)
foreach ($p in $pkgs) {
  Write-Host "== $($p.name) ($($p.id))"
  winget install --id $p.id -e --accept-package-agreements --accept-source-agreements --silent
}
Write-Host "== Audiveris : pas de paquet winget fiable ; télécharger l'installeur Windows depuis https://github.com/Audiveris/audiveris/releases (nécessite Java 21+, ex. winget install EclipseAdoptium.Temurin.21.JDK)"
Write-Host "== Banque d'orchestre libre : VSCO 2 Community Edition (CC0), SoundFont .sf2 : https://vis.versilstudios.com/vsco-community.html -> placer dans work/soundfonts/"
Write-Host "== Environnement Python"
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m atelier env
