import random
from Utils import Utils
#
# GROOVEMAKER
# makes the groove :-)
# bassline creator
#
class GrooveMaker(object):
        def __init__(self,eighths,key,beats,onbeat=False,bassmode=0,isModal = False,denominator = 4):
            # beats - the downbeats
            self.beats = beats
            self.eighths = eighths
            # onbeat bass plays only on beats
            # offbeat random plays on offbeats too
            self.onbeat = onbeat
            self.denominator = denominator
            # bassmode = 0 - random bass(offbeat) or half time bass(onbeat) [half time = plays only on downbeats]
            # bassmode = 1 - walking bass
            # bassmode = 2 - normal time bass(onbeat), no function on offbeat [ normal time = plays on all beats]
            # bassmode = 3 - double time bass(onbeat), no function on offbeat [ double time = plays on all beats, plus in the middle of the beats]
            # bassmode = 4 - shuffle bass
            # bassmode = 5 - bass riff
            # bassmode =99 - mutes  the bass
            self.bassmode = bassmode
            self.isModal = isModal # true = do not use chord root of tonic chord on 1 (offbeat) or do not at all  (onbeat)
            self.key = key # tonic of the scale
        
        # create random bass
        # consisting of eighth and sixteenth notes and rests
        # higher probability of rest on upbeats
        def process(self,chords):
            if self.bassmode == 1:
                return self._walking(chords)
            elif self.bassmode == 4 and self.denominator == 4:
                return self._shuffle(chords)
            elif self.bassmode == 99:
                text = ""
                i = 0
                while i < self.eighths:
                    text += " r8 "
                    i += 1    
                return text
            elif self.onbeat == True:
                return self._straight(chords)

            chord = chords[0]
            chordcnt = 0
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            mysum = 0
            result = ""
            beat = 0 # downbeat 1
            dur = 8
            play = 0
            note = ""
            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                if mysum in self.beats:
                    if mysum == self.beats[0]:  # beat 1
                        if self.isModal:
                            if chord[0] == self.key:
                                note = chord[1]
                            else:
                                note = chord[0]
                        else:    
                            note = chord[0]
                        play = 1 # always play on beat 1
                    else:
                        dur = 8
                        pdur = Utils.findDuration(dur)
                        play = 1
                        beat += 1 # next downbeat
                elif beat+1 < len(self.beats)  and mysum == (self.beats[beat+1] - 4): # one sixteenth before next downbeat
                    play = 1
                elif  mysum < self.beats[beat]+denominator: # between downbeat and upbeat
                    dur = 4
                    pdur = Utils.findDuration(dur)
                    donotplay = random.randint(0,3)
                    if donotplay > 0:
                        play = 0
                    else:
                        play = 1
                elif mysum == (self.beats[beat] + denominator): # upbeat
                    play = 0
                elif mysum > self.beats[len(self.beats)-1]: # after last downbeat
                    play = random.randint(0,1)
                else:
                    play = 0 # don't play between beat 2 and 3-8
                    if self.bassmode == 2 or self.bassmode == 3:
                        play = random.randint(0,1)
                if len(self.beats) > beat+1 and mysum > self.beats[beat+1]-denominator:
                    if len(chords) > chordcnt+1:
                        chordcnt += 1
                        chord = chords[chordcnt]

                if play > 0:
                    if note == "":
                        slot = random.randint(0,len(chord)-1)
                        note = chord[slot]
                    result += note
                    result += pdur
                    result += " "
                    note = ""
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
            return result

        # create onbeat bass
        # consisting of eighth notes and rests
        # bass notes only on downbeats (half time)
        # or also on upbeats (normal time)
        # or also in the middle between the beats (double time)
        def _straight(self,chords):
            denominator = self.denominator
            if denominator == 4:
                denominator = 16

            mysum = 0
            result = ""
            beat = 0 # downbeat 1
            dur = 8
            play = 1
            chord = chords[0]
            chordcnt = 0
            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                if mysum in self.beats: # this is a downbeat
                    play = 1
                elif self.bassmode == 3 and mysum == self.beats[beat] + 8:    
                    play = 1  # double time
                elif self.bassmode == 2 and mysum == self.beats[beat] + denominator:    
                    play = 1  # normal time
                elif self.bassmode == 3 and mysum == self.beats[beat] + denominator:    
                    play = 1  # double time
                elif self.bassmode == 3: # play in all slot
                    play = 1  # double time
                else:
                    play = 0 # rest
                if beat+1 < len(self.beats) and mysum == self.beats[beat+1]:
                    beat += 1 # next downbeat
                    if len(chords) > chordcnt+1:
                        chordcnt += 1
                        chord = chords[chordcnt]

                if play:
                    if self.isModal:
                        if chord[0] == self.key:
                            result += chord[1]
                        else:
                            result += chord[0]
                    else:    
                        note = chord[0]
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
            return result


        # create walking bass
        # consisting of quarter (or quaver)  notes without rests
        def _walking(self,chords):
            mysum = 0
            result = ""
            beat = 0
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            dur = denominator
            chord = chords[0]
            chordcnt = 0

            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                if mysum == 0:
                    if self.isModal:
                        if chord[0] == self.key:
                            result += chord[1]
                        else:
                            result += chord[0]
                    else:    
                        result += chord[0]
                    result += pdur
                    result += " "
                    mysum += dur
                    continue
                elif beat+1 < len(self.beats) and mysum == self.beats[beat+1]:
                    beat += 1
                if len(self.beats) > beat+1 and mysum > self.beats[beat+1]-denominator:
                    if len(chords) > chordcnt+1:
                        chordcnt += 1
                        chord = chords[chordcnt]
                slot = random.randint(0,len(chord)-1)
                note = chord[slot]
                result += note
                result += pdur
                result += " "
                mysum += dur
            return result

        # create shuffle bass
        # consisting of triplets of eighths without rests
        def _shuffle(self,chords):
            mysum = 0
            result = ""
            beat = 0
            dur = 16
            pdur = "8"
            chord = chords[0]
            chordcnt = 0
            denominator = self.denominator
            if denominator == 4:
                denominator = 16

            while mysum < (self.eighths * 8):
                loop = 2
                result += "\\times 2/3 { "
                while loop > 0:
                    loop -= 1
                    note = ""
                    if mysum == 0 and loop == 1:
                        if self.isModal:
                            if chord[0] == self.key:
                                note = chord[1]
                            else:
                                note = chord[0]
                        else:    
                            note = chord[0]
                        note += "4"    
                    elif beat+1 < len(self.beats) and mysum == self.beats[beat+1]:
                        beat += 1
                        chordcnt += 1
                        if len(chords) > chordcnt:
                            chord = chords[chordcnt]
                    if note == "":
                        slot = random.randint(0,len(chord)-1)
                        note = chord[slot]
                        if loop == 1:
                            note += "4"
                        else:    
                            note += pdur
                    result += note
                    result += " "
                    note = ""
                mysum += dur
                result += " } "
            return result

