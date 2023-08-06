
import random
from Utils import Utils

#
#
# HARMONYMAKER
#
#
class HarmonyMaker(object):
        notes = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
        notes_b = ['c','des','d','es','e','f','ges','g','as','a','bes','b']
        
        def __init__(self,eighths,beats,denominator,mode = 0):
                self.beats = beats
                self.eighths = eighths
                self.durations = self._findmymax()
                self.denominator = denominator
                self.mode = mode
                self.direction = 0 # none
                if self.mode == 1 or self.mode == 5:
                    self.direction = 1 # up
                elif self.mode == 2 or self.mode == 4:
                    self.direction = -1 # down

        def findNote(self,note):
            try:
                idx = self.notes.index(note)
                return idx
            except:
                try:
                    idx = self.notes_b.index(note)
                except:
                    print "Chord note %s not in list" % note
                    return 0
            return idx
            
            
        def _findmymax(self):
                durations = []
                old = -1
                mymax = 0
                for b in self.beats:
                    if old > -1:
                        tmp = b - old
                        if tmp > mymax:
                            mymax = tmp
                    old = b
                durs  = [4,8,16,32,64]
                for d in durs:
                    if d > mymax:
                        break
                    durations.append(d)
                return durations
            
        def getEmptyBar(self):
            text = ""
            i = 0
            while i < self.eighths:
                text += " r8 "
                i += 1    
            return text

        # this next method is
        # work in progress
        def _chordsVarLen(self,chords):
            result = ""
            bar = chords
            chord = bar[0]
            riffbar = ""
            mysum = 0
            beat = -1
            eighths = self.eighths * 8
            while mysum < eighths:
                print_dur =""
                dur = 16
                note = ""
                play = 1
                if mysum in self.beats:
                    beat += 1    
                    chord = bar[beat]    
                    note += "<"
                    for n in chord:
                        note += n
                        note += " "
                    note += ">"    
                    dur = 16 # quarter on downbeats
                else:
                    chord = bar[beat]    
                    note += "<"
                    for n in chord:
                        note += n
                        note += " "
                    note += ">"    

                    play = random.randint(0,1)
                    slot = 0 
                    if mysum+16 > eighths:
                        slot = 0
                    else:    
                        slot = random.randint(0,1)
                    if slot:
                        dur = 16 # quarter
                    else:
                        dur = 8  # or eighth  
                print_dur = Utils.findDuration(dur)
                if play == 0:
                    note = "r"
                riffbar += note
                riffbar += print_dur
                riffbar += " " 
                mysum += dur    
            return riffbar 


        # create a bar with chords only
        # chords are always onbeat
        # if useRest then chords will only be placed on 
        # the downbeats
        def makeChord(self,chords,useRest = True):
            result = ""
            if self.mode > 0 and self.mode < 6:
                return self._arpeggio(chords)
            # mode 7 is handled in LyMk.py
            elif self.mode == 8:
                return self._chordsVarLen(chords)    
            # this is mode 0
            cnt = 0
            pchord = ""
            denominator = 16 # quarter
            chord = chords[0]
            chordcnt = 0
            
            if self.denominator == 8:
                denominator = 8
                numerator = self.eighths
            else:
                numerator = int(self.eighths / 2)
            
            while cnt < numerator:
                pos = cnt * denominator
                if pos in self.beats or cnt == 0:
                    if pos > 0:
                        if len(chords) > chordcnt+1:
                            chordcnt += 1
                            chord = chords[chordcnt]

                    pchord = "<"
                    first = True
                    last_note = 0
                    octave = 0
                    if self.findNote(chord[0]) > 6:
                        octave = -1
                    start = octave
                    for n in chord:
                        if first == False:
                            pchord += " "
                        pchord += n
                        if first == False:
                            this_note = self.findNote(n)
                            if this_note < last_note:
                                octave += 1
                            c = start
                            while c < octave:
                                c += 1 
                                if c > 0:
                                    pchord += "'"

                        if octave < 0:
                            pchord += ","
                        first = False
                        last_note = self.findNote(n)
                    pchord += ">%d " % self.denominator
                    result += pchord
                else:
                    if useRest == False:
                        result += pchord
                    else:
                        result += " r%d " % self.denominator        
                cnt += 1    
            return result
        
        def _arpeggio(self,chords):
            # mode
            # 1 = noteUp
            # 2 = noteDown
            # 3 = random
            # 4 = bardownup
            # 5 = barupdown
            result = ""
            cnt = 0
            denominator = 16
            chord = chords[0]
            chordcnt = 0
            octave = 0            
            if self.denominator == 8:
                denominator = 8
                numerator = self.eighths
            else:
                numerator = int(self.eighths / 2)
            last_note = 0            
            offset = 0
            if self.mode == 4 or self.mode == 5:
                self.direction *= -1
            if self.direction  == -1:
                offset = len(chord)-1
                if self.findNote(chord[offset]) < 5:
                    octave = 1
                if numerator > 6:
                    octave += 1
            elif self.direction == 1:
                if self.findNote(chord[0]) >= 5:
                    octave = -1
                if numerator > 6:
                    octave -= 1
            while cnt < numerator:
                pos = cnt * denominator
                if pos in self.beats and pos != 0:
                    if len(chords) > chordcnt+1:
                        chordcnt += 1
                        chord = chords[chordcnt]
                        offset = 0
                        if self.direction == -1:
                            offset = len(chord)-1
                if self.mode == 3:
                    offset = random.randint(0,len(chord)-1)
                note = self.findNote(chord[offset])
                result += chord[offset]
                if self.direction == -1:
                    if note+(octave*12) > last_note and cnt > 0:
                        octave -= 1
                    if offset - 1 >= 0:
                        offset -= 1
                    else:
                        offset = len(chord)-1
                elif self.direction == 1:
                    if note+(octave*12) < last_note:
                        octave += 1
                    if offset + 1 < len(chord):
                        offset += 1
                    else:
                        offset = 0
                last_note = note+(octave*12)

                i = 0
                while octave > i:
                    result += "'"
                    i += 1 
                i = 0
                while octave < i:
                    result += ","
                    i -= 1
                result += "%d " % self.denominator
                cnt += 1
                
            return result

                
