\version "2.24.0"
% Squelette LilyPond d'un medley : une variable par pièce, un seul \score, parties générées par \book.
% Ici : un pont de quatre mesures qui module de fa majeur vers ré majeur (exemple pédagogique, à adapter).
\header { title = "Pont de transition" composer = "atelier-arrangement" tagline = ##f }

pont = \relative c'' {
  \key f \major \time 4/4
  \mark \default
  c2 bes4 a | g2 f | \key d \major fis2 g4 a | a1 \bar "||"
}
basse = \relative c {
  \key f \major \time 4/4
  f2 g | c2 c, | \key d \major d2 e | a1 \bar "||"
}

\score {
  <<
    \new Staff \with { instrumentName = "Violon I" } \pont
    \new Staff \with { instrumentName = "Violoncelle" } { \clef bass \basse }
  >>
  \layout { }
  \midi { \tempo 4 = 80 }
}
