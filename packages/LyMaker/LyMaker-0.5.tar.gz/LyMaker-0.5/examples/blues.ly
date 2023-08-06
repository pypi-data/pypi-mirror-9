\version "2.12.3"
\header {
 title = "blues"
  composer = "LyMaker"
  meter = "Allegretto"
}

global = { \time 4/4 }
Key = { \key c \major }

Riff = {
 c4 r4 bes4 r8 g8  |
  g4 g4 bes4 r4  |
}



RiffII = {
 g4 r8 bes4 r8 r8 r8  |
  bes4 bes8 bes8 g4 r4  |
}



TrumpetI =  {
% Part A
% range from fis, to c''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

TenorSaxI =  {
% Part A
% range from c to f''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthRI =  {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthLI = {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

RightI =  {
% Part A
% bar 1
\Riff

% bar 2

% bar 3
\Riff

% bar 4

% bar 5
\Riff

% bar 6

% bar 7
\Riff

% bar 8

% bar 9
\Riff

% bar 10

% bar 11
\Riff

% bar 12

}

LeftI = {
% Part A
% bar 1
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 2
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 3
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 4
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 5
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 6
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 7
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 8
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 9
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 10
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 11
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 12
<c e g bes>4 r4 <c e g bes>4 r4  | 
}

BassI = {
% Part A
% bar 1
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 2
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 3
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 4
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 5
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 6
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 7
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 8
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 9
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 10
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 11
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 12
c8 c8 c8 c8 c8 c8 c8 c8  | 
}

DrumsI = \drummode {
% Part A
% bar 1
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 2
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 3
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 4
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 5
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 6
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 7
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 8
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 9
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 10
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 11
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 12
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsI = \drummode {
% Part A
% bar 1
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 2
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 3
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 4
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 5
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 6
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 7
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 8
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 9
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 10
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 11
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 12
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetII =  {
% Part A
% range from fis, to c''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

TenorSaxII =  {
% Part A
% range from c to f''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthRII =  {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthLII = {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

RightII =  {
% Part A
% bar 1
\Riff

% bar 2

% bar 3
\Riff

% bar 4

% bar 5
\Riff

% bar 6

% bar 7
\Riff

% bar 8

% bar 9
\Riff

% bar 10

% bar 11
\Riff

% bar 12

}

LeftII = {
% Part A
% bar 1
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 2
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 3
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 4
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 5
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 6
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 7
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 8
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 9
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 10
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 11
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 12
<c e g bes>4 r4 <c e g bes>4 r4  | 
}

BassII = {
% Part A
% bar 1
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 2
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 3
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 4
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 5
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 6
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 7
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 8
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 9
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 10
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 11
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 12
c8 c8 c8 c8 c8 c8 c8 c8  | 
}

DrumsII = \drummode {
% Part A
% bar 1
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 2
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 3
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 4
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 5
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 6
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 7
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 8
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 9
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 10
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 11
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 12
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsII = \drummode {
% Part A
% bar 1
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 2
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 3
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 4
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 5
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 6
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 7
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 8
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 9
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 10
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 11
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 12
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetIII =  {
% Part A
% range from fis, to c''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

TenorSaxIII =  {
% Part A
% range from c to f''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthRIII =  {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthLIII = {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

RightIII =  {
% Part A
% bar 1
\Riff

% bar 2

% bar 3
\Riff

% bar 4

% bar 5
\Riff

% bar 6

% bar 7
\Riff

% bar 8

% bar 9
\Riff

% bar 10

% bar 11
\Riff

% bar 12

}

LeftIII = {
% Part A
% bar 1
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 2
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 3
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 4
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 5
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 6
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 7
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 8
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 9
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 10
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 11
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 12
<c e g bes>4 r4 <c e g bes>4 r4  | 
}

BassIII = {
% Part A
% bar 1
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 2
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 3
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 4
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 5
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 6
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 7
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 8
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 9
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 10
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 11
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 12
c8 c8 c8 c8 c8 c8 c8 c8  | 
}

DrumsIII = \drummode {
% Part A
% bar 1
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 2
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 3
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 4
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 5
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 6
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 7
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 8
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 9
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 10
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 11
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 12
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsIII = \drummode {
% Part A
% bar 1
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 2
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 3
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 4
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 5
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 6
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 7
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 8
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 9
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 10
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 11
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 12
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetIV =  {
% Part A
% range from fis, to c''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

TenorSaxIV =  {
% Part A
% range from c to f''
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthRIV =  {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

SynthLIV = {
% Part A
% bar 1
 | 
% bar 2
 | 
% bar 3
 | 
% bar 4
 | 
% bar 5
 | 
% bar 6
 | 
% bar 7
 | 
% bar 8
 | 
% bar 9
 | 
% bar 10
 | 
% bar 11
 | 
% bar 12
 | 
}

RightIV =  {
% Part A
% bar 1
\Riff

% bar 2

% bar 3
\Riff

% bar 4

% bar 5
\Riff

% bar 6

% bar 7
\Riff

% bar 8

% bar 9
\Riff

% bar 10

% bar 11
\Riff

% bar 12

}

LeftIV = {
% Part A
% bar 1
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 2
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 3
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 4
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 5
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 6
<f a c' es'>4 r4 <f a c' es'>4 r4  | 
% bar 7
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 8
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 9
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 10
<g b d' f'>4 r4 <g b d' f'>4 r4  | 
% bar 11
<c e g bes>4 r4 <c e g bes>4 r4  | 
% bar 12
<c e g bes>4 r4 <c e g bes>4 r4  | 
}

BassIV = {
% Part A
% bar 1
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 2
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 3
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 4
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 5
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 6
f8 f8 f8 f8 f8 f8 f8 f8  | 
% bar 7
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 8
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 9
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 10
g8 g8 g8 g8 g8 g8 g8 g8  | 
% bar 11
c8 c8 c8 c8 c8 c8 c8 c8  | 
% bar 12
c8 c8 c8 c8 c8 c8 c8 c8  | 
}

DrumsIV = \drummode {
% Part A
% bar 1
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 2
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 3
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 4
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 5
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 6
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 7
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 8
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 9
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 10
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 11
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 12
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsIV = \drummode {
% Part A
% bar 1
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 2
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 3
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 4
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 5
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 6
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 7
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 8
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 9
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 10
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 11
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 12
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}


A = {
<c e g bes>4 r4 <c e g bes>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 <f a c' es'>4 r4 <f a c' es'>4 r4  |
 <f a c' es'>4 r4 <f a c' es'>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 <g b d' f'>4 r4 <g b d' f'>4 r4  |
 <g b d' f'>4 r4 <g b d' f'>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 <c e g bes>4 r4 <c e g bes>4 r4  |
 
}

harmonies = {
    \A
    \A
    \A
    \A
    }
Trumpet = \transpose c c' {
\clef treble
\global
\Key 
\TrumpetI   \TrumpetII   \TrumpetIII   \TrumpetIV   
}
Right = \transpose c c' {
\clef treble
\global
\Key
\RightI   \RightII   \RightIII   \RightIV   
}
Left = {
\clef bass
\global
\Key
\LeftI   \LeftII   \LeftIII   \LeftIV   
}
Bass = \transpose c c, {
\clef "bass_8"
\global
\Key
\BassI   \BassII   \BassIII   \BassIV   
}
Drums = \drummode {
\global
\voiceOne
\DrumsI   \DrumsII   \DrumsIII   \DrumsIV   
}
Cymbals = \drummode {
\global
\voiceTwo
\CymbalsI   \CymbalsII   \CymbalsIII   \CymbalsIV   
}
SynthR = \transpose c c'' {
\clef treble
\global
\Key
\SynthRI   \SynthRII   \SynthRIII   \SynthRIV   
}
SynthL = {
\clef bass
\global
\Key
\SynthLI   \SynthLII   \SynthLIII   \SynthLIV   
}
TenorSax = \transpose c c' {
\clef treble
\global
\key d \major
\transposition bes
\TenorSaxI   \TenorSaxII   \TenorSaxIII   \TenorSaxIV   
}

piano = {
<<
\set PianoStaff.instrumentName = #"Piano"
\set PianoStaff.midiInstrument = #"acoustic grand"
\new Staff = "upper" \Right
\new Staff = "lower" \Left
>>
}

synth = {
<<
\set PianoStaff.instrumentName = #"Synthesizer"
\set PianoStaff.midiInstrument = #"english horn"
\new Staff = "upper" \SynthR
\new Staff = "lower" \SynthL
>>
}

trumpet = {
\set Staff.instrumentName = #"Trumpet in C"
\set Staff.midiInstrument = #"trumpet"
<<
\Trumpet
>>
}

tenorSax = {
\set Staff.instrumentName = #"Tenor Sax"
\set Staff.midiInstrument = #"tenor sax"
<<
\TenorSax
>>
}

bass = {
\set Staff.instrumentName = #"Bass"
\set Staff.midiInstrument = #"acoustic bass"
<<
\Bass
>>
}

drumContents = {
<<
\set DrumStaff.instrumentName = #"Drums"
\new DrumVoice \Cymbals
\new DrumVoice \Drums
>>
}

\score {
 <<
  \new StaffGroup
  <<
   \new PianoStaff = "piano" \piano
   \new PianoStaff = "synthesizer" \synth
   \new Staff = "trumpet" \trumpet
   \new Staff = "tenorSax" \tenorSax
   \new Staff = "bass" \bass
   \new ChordNames {
      \harmonies
   }
   \new DrumStaff \drumContents
  >>
 >>
 \layout { }
 \midi {
   \context {
  \Score
   tempoWholesPerMinute = #(ly:make-moment 100 4)
    }
 }
}
