import sys, getopt,os
import random
from Utils import Utils
from ScaleUtil import Scale,ScaleUtil

class MelodyMaker(object):

    down_durations  = [16,32]
    up_durations = [8,16]

    def __init__(self,eighths,beats,denominator,scale,tempo,mode = 0,synthMode = 0):
        self.beats = beats
        self.eighths = eighths
        self.denominator = denominator
        self.scale = scale
        self.mode = mode
        self.tempo = tempo
        self.synthMode = synthMode


    def process(self,chords):
        melody = ""
        counterpoint = ""
        # mode
        # 1 - piano left hand = melody, piano right = counterpoint
        # 2 - trumpet = melody, saxophone = counterpoint
        # 3 = trumpet solo
        # 4 = saxophone solo
        # 5 - sax = melody, piano counterpoint
        # 6 - piano solo
        # 99 = mute
        if self.mode == 3:
            melody,counterpoint = self._solo(chords)
        elif self.mode == 4 and self.synthMode == 0:
            melody,counterpoint = self._solo(chords,2) # transpose sax + 2 semitones
        elif self.mode == 4 and self.synthMode > 0:
            melody,counterpoint = self._solo(chords,0) 
        elif self.mode == 1:
            melody,counterpoint = self._solo(chords,0,1,0)
        elif self.mode == 2 and self.synthMode == 0:
            melody,counterpoint = self._solo(chords,0,1,2)
        elif self.mode == 2 and self.synthMode > 0:
            melody,counterpoint = self._solo(chords,0,1,0)
        elif self.mode == 5 and self.synthMode == 0:
            melody,counterpoint = self._solo(chords,2,1,0)
        elif self.mode == 5 and self.synthMode > 0:
            melody,counterpoint = self._solo(chords,0,1,0)
        elif self.mode == 6:
            melody,counterpoint = self._solo(chords,0,0,0)
        elif self.mode == 99 or self.mode == 0:
            melody = self._getEmptyBar()
            counterpoint = self._getEmptyBar()
        return melody,counterpoint

    def _getEmptyBar(self):
        text = ""
        i = 0
        while i < self.eighths:
            text += " r8 "
            i += 1    
        return text

    def _findNote(self,note):
        index = self.scale.find(note) # returns 0 -6
        if index == -1:
            index = self.scale.find(note+12)
            return index
        else:
            return index

    def _fetchChordNotes(self,chords):
        notes = []
        offset = 0
        for beat in self.beats:
            chord = chords[offset]
            x = random.randint(0,len(chord)-1)
            note = chord[x]
            notes.append(note)
            if offset+1 < len(chords):
                offset += 1
        return notes

    def _getMaxStep(self):
        if self.scale.isLilypondScale(self.scale.scale_type):
            return 2
        else:
            return 4


    def _findNear(self,key):
        note = self.scale.get(0)
        if key < note:
            key += 12
        if key < note + 11:
            key += 1
        else:
            key = note
        index = self.scale.find(key) # returns 0 - 6
        if index == -1:
            if key > note +1:
                key -= 2
            else:
                key = note + 11
            index = self.scale.find(key) # returns 0 - 6
            if index == -1:
                index = note
        return index

    def _getPropability(self):
        prop = 1
        if (240-self.tempo) >= 40:
            prop = int((240 -self.tempo) * 0.025)
        return prop

    def _solo(self,chords,transpose = 0,counterpoint = 0,trans_cp = 0):
        mysum = 0
        mysumC = 0
        result = ""
        resultC = ""
        dur = 8
        durC = 8
        play = 0
        note = ""
        last_note = -1
        last_noteC = -1
        chord_notes = self._fetchChordNotes(chords)
        chord = chords[0]
        if counterpoint == 0:
            resultC = self._getEmptyBar()
        offset = 0
        offsetC = 0
        chordIndex = 0
        while mysum < (self.eighths * 8):
            if mysum in self.beats:
                dur = random.randint(0,len(self.down_durations)-1)
                dur = self.down_durations[dur]
                if  (mysum +dur) > self.eighths*8:
                    dur = (self.eighths*8) - mysum
                pdur = Utils.findDuration(dur)
                note = chord_notes[offset]
                key,flat = ScaleUtil.getNoteFromName(note) # returns 0 - 11
                index = self.scale.find(key) # returns 0 - 6
                if index == -1:
                    index = self.scale.find(key+12) # returns 0 - 6
                    if index == -1:
                        print "WARNING melody: chord note %s is not in scale" % (note)
                        index = self._findNear(key)
                note = self.scale.getNameFromNote(key+transpose)
                last_note = self.scale.get(index)
                offset += 1
            else:
                dur = random.randint(0,len(self.up_durations)-1)
                dur = self.up_durations[dur]
                if  (mysum +dur) > self.eighths*8:
                    dur = (self.eighths*8) - mysum
                pdur = Utils.findDuration(dur)
                play = random.randint(0,self._getPropability())
                index = -1
                if play > 0:
                    while index == -1:
                        max_step = self._getMaxStep()
                        x = random.randint(1,max_step)
                        old_index = self._findNote(last_note)
                        index = self._findNote(last_note + x)
                        if index == -1  or index < old_index:
                            index = self._findNote(last_note - x)
                        if index == -1  :
                            continue
                        note_no = self.scale.get(index)
                        note = self.scale.getNameFromNote(note_no+transpose) 
                    last_note = self.scale.get(index)
                    #print "Note %s, index %d, last_note %d" % (note,index,last_note)
                else:
                    note = "r"
            result += note
            if note != "r" and (self.mode != 1 and self.mode != 6):
                result += "'"
            result += pdur
            result += " "
            if counterpoint > 0 and mysumC < (self.eighths*8):
                if mysumC in self.beats:
                    durC = random.randint(0,len(self.down_durations)-1)
                    durC = self.down_durations[durC]
                    if  (mysumC +durC) > self.eighths*8:
                        durC = (self.eighths*8) - mysumC
                    pdur = Utils.findDuration(durC)
                    note = chord_notes[offsetC]
                    x = note
                    while x == note:
                        x = random.randint(0,len(chords[chordIndex])-1)
                        x = chords[chordIndex][x]
                    key,flat = ScaleUtil.getNoteFromName(x) # returns 0 - 11
                    index = self.scale.find(key) # returns 0 - 6
                    if index == -1:
                        index = self.scale.find(key+12) # returns 0 - 6
                        if index == -1:
                            print "WARNING counterpoint: chord note %s is not in scale" % (x)
                            index = self._findNear(key)
                    note = self.scale.getNameFromNote(key+trans_cp)
                    last_noteC = self.scale.get(index)
                    if chordIndex+1 < len(chords):
                        chordIndex += 1
                    offsetC += 1
                else:
                    durC = random.randint(0,len(self.down_durations)-1)
                    durC = self.down_durations[durC]
                    if  (mysumC +durC) > self.eighths*8:
                        durC = (self.eighths*8) - mysumC
                    pdur = Utils.findDuration(durC)
                    play = random.randint(0,3)
                    index = -1
                    if play > 0:
                        while index == -1:
                            max_step = self._getMaxStep()
                            x = random.randint(1,max_step)
                            index = self._findNote(last_noteC + x)
                            old_index = self._findNote(last_noteC)
                            if index == -1  or index < old_index:
                                index = self._findNote(last_noteC - x)
                            if index == -1:
                                continue
                            note_no = self.scale.get(index)
                            note = self.scale.getNameFromNote(note_no+trans_cp) 
                        last_noteC = self.scale.get(index)
                    else:
                        note = "r"
                resultC += note
                resultC += pdur
                resultC += " "
                mysumC += durC
            mysum += dur                    
        if counterpoint > 0 and mysumC < (self.eighths*8):
            resultC += "r"
            durC = (self.eighths*8) - mysumC
            pdur = Utils.findDuration(durC)
            resultC += pdur
            resultC += " "
        return result,resultC


                


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "k:", ["key="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)
    key = "c major"
    for o, a in opts:
        if o in ("-k", "--key"):
            key = a
    
    seq = ScaleUtil()
    seq.setKey(key)
    scale = seq.scale
    prog = MelodyMaker(8,[0,32],4,scale,100,3)
    chords = []
    chords.append(['c','e','g'])
    print prog._solo(chords)

if __name__ == "__main__":
    main()
