\version "2.12.3"
\header {
 title = "rock"
  composer = "LyMaker"
  meter = "Vivace"
}

global = { \time 4/4 }
Key = { \key c \major }

Riff = {
 c4 r8 r8 g4 g4  |
  c4 r4 c4 r8 r8  |
}



RiffII = {
 c4 e4 g4 r4  |
  c4 r8 r4 c4 r8  |
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

}

LeftI = {
% Part A
% bar 1
<c e g>4 r4 <c e g>4 r4  | 
% bar 2
<c e g>4 r4 <c e g>4 r4  | 
% bar 3
<a c' e'>4 r4 <a c' e'>4 r4  | 
% bar 4
<a c' e'>4 r4 <a c' e'>4 r4  | 
% bar 5
<d f a>4 r4 <d f a>4 r4  | 
% bar 6
<d f a>4 r4 <d f a>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<f a c'>4 r4 <f a c'>4 r4  | 
}

BassI = {
% Part A
% bar 1
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 2
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 3
a8 r8 a8 r8 a8 r8 a8 r8  | 
% bar 4
a8 r8 a8 r8 a8 r8 a8 r8  | 
% bar 5
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 6
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
f8 r8 f8 r8 f8 r8 f8 r8  | 
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
}

TrumpetII =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

TenorSaxII =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthRII =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthLII = {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

RightII =  {
% Part B
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

% bar 13
\Riff

% bar 14

% bar 15
\Riff

% bar 16

}

LeftII = {
% Part B
% bar 1
<c e g>4 r4 <c e g>4 r4  | 
% bar 2
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 3
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 4
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 5
<c e g>4 r4 <c e g>4 r4  | 
% bar 6
<e g b>4 r4 <e g b>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 9
<a c' e'>4 r4 <a c' e'>4 r4  | 
% bar 10
<d f a>4 r4 <d f a>4 r4  | 
% bar 11
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 12
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 13
<c e g>4 r4 <c e g>4 r4  | 
% bar 14
<e g b>4 r4 <e g b>4 r4  | 
% bar 15
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 16
<g b d'>4 r4 <g b d'>4 r4  | 
}

BassII = {
% Part B
% bar 1
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 2
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 3
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 4
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 5
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 6
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 9
a8 r8 a8 r8 a8 r8 a8 r8  | 
% bar 10
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 11
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 12
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 13
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 14
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 15
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 16
g8 r8 g8 r8 g8 r8 g8 r8  | 
}

DrumsII = \drummode {
% Part B
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
% bar 13
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 14
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 15
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 16
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsII = \drummode {
% Part B
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
% bar 13
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 14
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 15
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 16
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetIII =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

TenorSaxIII =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthRIII =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthLIII = {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

RightIII =  {
% Part C
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

% bar 13
\Riff

% bar 14

% bar 15
\Riff

% bar 16

}

LeftIII = {
% Part C
% bar 1
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 2
<e g b>4 r4 <e g b>4 r4  | 
% bar 3
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 4
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 5
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 6
<e g b>4 r4 <e g b>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 9
<c e g>4 r4 <c e g>4 r4  | 
% bar 10
<d f a>4 r4 <d f a>4 r4  | 
% bar 11
<b d' f'>4 r4 <b d' f'>4 r4  | 
% bar 12
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 13
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 14
<e g b>4 r4 <e g b>4 r4  | 
% bar 15
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 16
<c e g>4 r4 <c e g>4 r4  | 
}

BassIII = {
% Part C
% bar 1
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 2
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 3
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 4
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 5
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 6
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 9
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 10
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 11
b8 r8 b8 r8 b8 r8 b8 r8  | 
% bar 12
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 13
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 14
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 15
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 16
c8 r8 c8 r8 c8 r8 c8 r8  | 
}

DrumsIII = \drummode {
% Part C
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
% bar 13
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 14
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 15
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 16
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsIII = \drummode {
% Part C
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
% bar 13
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 14
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 15
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 16
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetIV =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

TenorSaxIV =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthRIV =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthLIV = {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

RightIV =  {
% Part B
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

% bar 13
\Riff

% bar 14

% bar 15
\Riff

% bar 16

}

LeftIV = {
% Part B
% bar 1
<c e g>4 r4 <c e g>4 r4  | 
% bar 2
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 3
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 4
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 5
<c e g>4 r4 <c e g>4 r4  | 
% bar 6
<e g b>4 r4 <e g b>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 9
<a c' e'>4 r4 <a c' e'>4 r4  | 
% bar 10
<d f a>4 r4 <d f a>4 r4  | 
% bar 11
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 12
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 13
<c e g>4 r4 <c e g>4 r4  | 
% bar 14
<e g b>4 r4 <e g b>4 r4  | 
% bar 15
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 16
<g b d'>4 r4 <g b d'>4 r4  | 
}

BassIV = {
% Part B
% bar 1
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 2
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 3
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 4
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 5
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 6
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 9
a8 r8 a8 r8 a8 r8 a8 r8  | 
% bar 10
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 11
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 12
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 13
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 14
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 15
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 16
g8 r8 g8 r8 g8 r8 g8 r8  | 
}

DrumsIV = \drummode {
% Part B
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
% bar 13
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 14
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 15
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 16
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsIV = \drummode {
% Part B
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
% bar 13
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 14
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 15
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 16
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetV =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

TenorSaxV =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthRV =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthLV = {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

RightV =  {
% Part C
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

% bar 13
\Riff

% bar 14

% bar 15
\Riff

% bar 16

}

LeftV = {
% Part C
% bar 1
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 2
<e g b>4 r4 <e g b>4 r4  | 
% bar 3
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 4
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 5
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 6
<e g b>4 r4 <e g b>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 9
<c e g>4 r4 <c e g>4 r4  | 
% bar 10
<d f a>4 r4 <d f a>4 r4  | 
% bar 11
<b d' f'>4 r4 <b d' f'>4 r4  | 
% bar 12
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 13
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 14
<e g b>4 r4 <e g b>4 r4  | 
% bar 15
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 16
<c e g>4 r4 <c e g>4 r4  | 
}

BassV = {
% Part C
% bar 1
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 2
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 3
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 4
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 5
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 6
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 9
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 10
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 11
b8 r8 b8 r8 b8 r8 b8 r8  | 
% bar 12
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 13
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 14
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 15
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 16
c8 r8 c8 r8 c8 r8 c8 r8  | 
}

DrumsV = \drummode {
% Part C
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
% bar 13
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 14
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 15
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 16
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsV = \drummode {
% Part C
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
% bar 13
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 14
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 15
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 16
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetVI =  {
% Part D
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
}

TenorSaxVI =  {
% Part D
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
}

SynthRVI =  {
% Part D
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
}

SynthLVI = {
% Part D
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
}

RightVI =  {
% Part D
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

}

LeftVI = {
% Part D
% bar 1
<e g b>4 r4 <e g b>4 r4  | 
% bar 2
<e g b>4 r4 <e g b>4 r4  | 
% bar 3
<a c' e'>4 r4 <a c' e'>4 r4  | 
% bar 4
<a c' e'>4 r4 <c e g>4 r4  | 
% bar 5
<d f a>4 r4 <d f a>4 r4  | 
% bar 6
<d f a>4 r4 <d f a>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<f a c'>4 r4 <f a c'>4 r4  | 
}

BassVI = {
% Part D
% bar 1
e8 r8 r8 r8 e8 r8 r8 r8  | 
% bar 2
e8 r8 r8 r8 e8 r8 r8 r8  | 
% bar 3
a8 r8 r8 r8 a8 r8 r8 r8  | 
% bar 4
a8 r8 r8 r8 c8 r8 r8 r8  | 
% bar 5
d8 r8 r8 r8 d8 r8 r8 r8  | 
% bar 6
d8 r8 r8 r8 d8 r8 r8 r8  | 
% bar 7
f8 r8 r8 r8 f8 r8 r8 r8  | 
% bar 8
f8 r8 r8 r8 f8 r8 r8 r8  | 
}

DrumsVI = \drummode {
% Part D
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
}

CymbalsVI = \drummode {
% Part D
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
}

TrumpetVII =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

TenorSaxVII =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthRVII =  {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthLVII = {
% Part B
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

RightVII =  {
% Part B
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

% bar 13
\Riff

% bar 14

% bar 15
\Riff

% bar 16

}

LeftVII = {
% Part B
% bar 1
<c e g>4 r4 <c e g>4 r4  | 
% bar 2
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 3
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 4
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 5
<c e g>4 r4 <c e g>4 r4  | 
% bar 6
<e g b>4 r4 <e g b>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 9
<a c' e'>4 r4 <a c' e'>4 r4  | 
% bar 10
<d f a>4 r4 <d f a>4 r4  | 
% bar 11
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 12
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 13
<c e g>4 r4 <c e g>4 r4  | 
% bar 14
<e g b>4 r4 <e g b>4 r4  | 
% bar 15
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 16
<g b d'>4 r4 <g b d'>4 r4  | 
}

BassVII = {
% Part B
% bar 1
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 2
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 3
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 4
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 5
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 6
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 9
a8 r8 a8 r8 a8 r8 a8 r8  | 
% bar 10
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 11
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 12
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 13
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 14
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 15
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 16
g8 r8 g8 r8 g8 r8 g8 r8  | 
}

DrumsVII = \drummode {
% Part B
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
% bar 13
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 14
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 15
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 16
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsVII = \drummode {
% Part B
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
% bar 13
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 14
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 15
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 16
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}

TrumpetVIII =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

TenorSaxVIII =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthRVIII =  {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

SynthLVIII = {
% Part C
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
% bar 13
 | 
% bar 14
 | 
% bar 15
 | 
% bar 16
 | 
}

RightVIII =  {
% Part C
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

% bar 13
\Riff

% bar 14

% bar 15
\Riff

% bar 16

}

LeftVIII = {
% Part C
% bar 1
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 2
<e g b>4 r4 <e g b>4 r4  | 
% bar 3
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 4
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 5
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 6
<e g b>4 r4 <e g b>4 r4  | 
% bar 7
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 8
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 9
<c e g>4 r4 <c e g>4 r4  | 
% bar 10
<d f a>4 r4 <d f a>4 r4  | 
% bar 11
<b d' f'>4 r4 <b d' f'>4 r4  | 
% bar 12
<g b d'>4 r4 <g b d'>4 r4  | 
% bar 13
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 14
<e g b>4 r4 <e g b>4 r4  | 
% bar 15
<f a c'>4 r4 <f a c'>4 r4  | 
% bar 16
<c e g>4 r4 <c e g>4 r4  | 
}

BassVIII = {
% Part C
% bar 1
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 2
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 3
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 4
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 5
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 6
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 7
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 8
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 9
c8 r8 c8 r8 c8 r8 c8 r8  | 
% bar 10
d8 r8 d8 r8 d8 r8 d8 r8  | 
% bar 11
b8 r8 b8 r8 b8 r8 b8 r8  | 
% bar 12
g8 r8 g8 r8 g8 r8 g8 r8  | 
% bar 13
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 14
e8 r8 e8 r8 e8 r8 e8 r8  | 
% bar 15
f8 r8 f8 r8 f8 r8 f8 r8  | 
% bar 16
c8 r8 c8 r8 c8 r8 c8 r8  | 
}

DrumsVIII = \drummode {
% Part C
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
% bar 13
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 14
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 15
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
% bar 16
bd16 r16 r16 r16 sn16 r16 r16 r16 bd16 r16 r16 r16 sn16 r16 r16 r16  | 
}

CymbalsVIII = \drummode {
% Part C
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
% bar 13
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 14
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 15
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
% bar 16
hh16 hh16 hh16 hh16 r16 r16 r16 r16 hh16 hh16 hh16 hh16 r16 r16 r16 r16  | 
}


A = {
<c e g>4 r4 <c e g>4 r4  |
 <c e g>4 r4 <c e g>4 r4  |
 <a c' e'>4 r4 <a c' e'>4 r4  |
 <a c' e'>4 r4 <a c' e'>4 r4  |
 <d f a>4 r4 <d f a>4 r4  |
 <d f a>4 r4 <d f a>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 
}

B = {
<c e g>4 r4 <c e g>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <c e g>4 r4 <c e g>4 r4  |
 <e g b>4 r4 <e g b>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <a c' e'>4 r4 <a c' e'>4 r4  |
 <d f a>4 r4 <d f a>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <c e g>4 r4 <c e g>4 r4  |
 <e g b>4 r4 <e g b>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 
}

C = {
<f a c'>4 r4 <f a c'>4 r4  |
 <e g b>4 r4 <e g b>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <e g b>4 r4 <e g b>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <c e g>4 r4 <c e g>4 r4  |
 <d f a>4 r4 <d f a>4 r4  |
 <b d' f'>4 r4 <b d' f'>4 r4  |
 <g b d'>4 r4 <g b d'>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <e g b>4 r4 <e g b>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <c e g>4 r4 <c e g>4 r4  |
 
}

D = {
<e g b>4 r4 <e g b>4 r4  |
 <e g b>4 r4 <e g b>4 r4  |
 <a c' e'>4 r4 <a c' e'>4 r4  |
 <a c' e'>4 r4 <c e g>4 r4  |
 <d f a>4 r4 <d f a>4 r4  |
 <d f a>4 r4 <d f a>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 <f a c'>4 r4 <f a c'>4 r4  |
 
}

harmonies = {
    \A
    \B
    \C
    \B
    \C
    \D
    \B
    \C
    }
Trumpet = \transpose c c' {
\clef treble
\global
\Key 
\TrumpetI   \TrumpetII   \TrumpetIII   \TrumpetIV   \TrumpetV   \TrumpetVI   \TrumpetVII   \TrumpetVIII   
}
Right = \transpose c c' {
\clef treble
\global
\Key
\RightI   \RightII   \RightIII   \RightIV   \RightV   \RightVI   \RightVII   \RightVIII   
}
Left = {
\clef bass
\global
\Key
\LeftI   \LeftII   \LeftIII   \LeftIV   \LeftV   \LeftVI   \LeftVII   \LeftVIII   
}
Bass = \transpose c c, {
\clef "bass_8"
\global
\Key
\BassI   \BassII   \BassIII   \BassIV   \BassV   \BassVI   \BassVII   \BassVIII   
}
Drums = \drummode {
\global
\voiceOne
\DrumsI   \DrumsII   \DrumsIII   \DrumsIV   \DrumsV   \DrumsVI   \DrumsVII   \DrumsVIII   
}
Cymbals = \drummode {
\global
\voiceTwo
\CymbalsI   \CymbalsII   \CymbalsIII   \CymbalsIV   \CymbalsV   \CymbalsVI   \CymbalsVII   \CymbalsVIII   
}
SynthR = \transpose c c'' {
\clef treble
\global
\Key
\SynthRI   \SynthRII   \SynthRIII   \SynthRIV   \SynthRV   \SynthRVI   \SynthRVII   \SynthRVIII   
}
SynthL = {
\clef bass
\global
\Key
\SynthLI   \SynthLII   \SynthLIII   \SynthLIV   \SynthLV   \SynthLVI   \SynthLVII   \SynthLVIII   
}
TenorSax = \transpose c c' {
\clef treble
\global
\key d \major
\transposition bes
\TenorSaxI   \TenorSaxII   \TenorSaxIII   \TenorSaxIV   \TenorSaxV   \TenorSaxVI   \TenorSaxVII   \TenorSaxVIII   
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
   tempoWholesPerMinute = #(ly:make-moment 140 4)
    }
 }
}
