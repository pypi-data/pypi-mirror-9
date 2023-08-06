import sys, getopt,os
import random
from copy import deepcopy

note_names = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b'] 
note_names2 = ['c','des','d','es','e','f','ges','g','as','a','bes','b'] 


class Scale(object):
    
    major = [0,2,4,5,7,9,11]
    minor = [0,2,3,5,7,8,10]
    minorExt = [0,2,3,5,7,8,9,10,11]
    dorian = [0,2,3,5,7,9,10]
    phrygian = [0,1,3,5,7,8,10]
    lydian = [0,2,4,6,7,9,11]
    mixolydian = [0,2,4,5,7,9,10]
    aeolian = [0,2,3,5,7,8,10]
    locrian = [0,1,3,5,6,8,10]    
    pentatonic = [0,2,4,7,9]
    japanese = [0,1,5,7,10]
    blues = [0,2,3,4,7,9]
    bluesMin = [0,3,5,6,7,10]
    twelvetone = [0,1,2,3,4,5,6,7,8,9,10,11]
    dim = [0,2,3,5,6,8,10]
    aug = [0,2,4,5,8,9,10]
    augmaj = [0,2,4,5,8,9,11]
    
    
    def __init__(self):
        self.key = 0
        self.scale_type = self.major
        self.notes = []
        self.flat = False

    def initialize(self,key,stype,flat):
        self.key = key
        self.scale_type = stype
        self._setNotes()
        self.flat = flat
    
    def _setNotes(self):
        self.notes = []
        for i in self.scale_type:
            self.notes.append(self.key + i)

    def find(self,key):
        index = -1
        try:
            index = self.notes.index(key)
        except ValueError:
            index = -1
        return index
    
    def get(self,index):
        if index > len(self.notes)-1:
            return -1
        else:
            return self.notes[index]
        
    def getNameFromNote(self,note):
        notes = note_names
        if self.flat:
            notes = note_names2
        if note >= 0 and note < 12:
            return notes[note]
        elif note > 11 and note < 24:
            note -= 12
            return notes[note]
        elif note > 23 and note < 36:
            note -= 24
            return notes[note]
        else:
            return "unknown%s" % note

    @classmethod
    def getNoteName(self,note,flat=False):
        notes = note_names
        if flat:
            notes = note_names2
        if note >= 0 and note < 12:
            return notes[note]
        elif note > 11 and note < 24:
            note -= 12
            return notes[note]
        elif note > 23 and note < 36:
            note -= 24
            return notes[note]
        else:
            return "unknown%s" % note
        
    def getTypeNameFromType(self,stype):
        if stype == self.major:
            return "major"
        elif stype == self.minor:
            return "minor"
        elif stype == self.minorExt:
            return "minor"
        elif stype == self.aeolian:
            return "aeolian"
        elif stype == self.locrian:
            return "locrian"
        elif stype == self.dorian:
            return "dorian"
        elif stype == self.lydian:
            return "lydian"
        elif stype == self.mixolydian:
            return "mixolydian"
        elif stype == self.phrygian:
            return "phrygian"
        elif stype == self.pentatonic:
            return "pentatonic"
        elif stype == self.blues:
            return "blues"
        elif stype == self.bluesMin:
            return "blues minor"
        elif stype == self.japanese:
            return "japanese"
        elif stype == self.twelvetone:
            return "twelve-tone"
        elif stype == self.dim:
            return "dim"
        elif stype == self.aug:
            return "aug"
        elif stype == self.augmaj:
            return "augmaj"
        else:
            return "unknown"

    @classmethod
    def isLilypondScale(self,stype):
        if stype == self.major:
            return True
        elif stype == self.minor:
            return True
        elif stype == self.minorExt:
            return False
        elif stype == self.aeolian:
            return True
        elif stype == self.locrian:
            return True
        elif stype == self.dorian:
            return True
        elif stype == self.lydian:
            return True
        elif stype == self.mixolydian:
            return True
        elif stype == self.phrygian:
            return True
        elif stype == self.pentatonic:
            return False
        elif stype == self.blues:
            return False
        elif stype == self.bluesMin:
            return False
        elif stype == self.japanese:
            return False
        elif stype == self.twelvetone:
            return False
        elif stype == self.dim:
            return False
        elif stype == self.aug:
            return False
        elif stype == self.augmaj:
            return False
        else:
            return False
        
    def asString(self):
        buf = "scale: %s %s\n" % (self.getNameFromNote(self.key),self.getTypeNameFromType(self.scale_type))
        for n in self.notes:
            buf += self.getNameFromNote(n)
            buf +=","
        buf += "\n"    
        return buf


class ScaleUtil(object):

    def __init__(self):
        self.chords = []
        self.scale = Scale()
        self.chordNames = []

    def setKey(self,key):
        note,stype,flat = self.getScaleFromString(key)
        self.scale.initialize(note,stype,flat)
        self.chords = []
        self.chordNames = []

    def _isPlainMajor(self,chord,seventh=False):
        length = 3
        if seventh == True:
            length = 4
        if len(chord) != length:
            return False
        root = chord[0]
        second = chord[1]
        if second != root +4:
            return False
        third = chord[2]
        if third != root +7:
            return False
        if seventh == True:
            if chord[3] != root + 10 and chord[3] != root + 11:
                return False
        return True

    def _isPlainMinor(self,chord,seventh= False):
        length = 3
        if seventh == True:
            length = 4
        if len(chord) != length:
            return False
        root = chord[0]
        second = chord[1]
        if second != root +3:
            return False
        third = chord[2]
        if third != root +7:
            return False
        if seventh == True:
            if chord[3] != root + 10:
                return False
        return True
        
    def getChords(self):
	if len(self.chords) == 0:
	    self._findChords()
        text = self.scale.asString()
        text += "  CHORDS\n"
        i = 0
        for n in self.chordNames:
            ch = self.chords[i]
            if self._isPlainMajor(ch) or self._isPlainMinor(ch):
                text += "**" 
            elif self._isPlainMajor(ch,True) or self._isPlainMinor(ch,True):
                text += " *"
            else:
                text += "  "
            text += n
            text += " < "
            for note in ch:
                text += self.scale.getNameFromNote(note)
                text += " "
            text += ">\n"
            i += 1
        return text

    def _findChords(self):
        chords = []
        for n in self.scale.notes:
            for o in self.scale.notes:
                if o == n:
                    continue
                elif o < n:
                    if o+12 == n:
                        continue
                    o += 12
                for p in self.scale.notes:
                    if p == o or p == n:
                        continue
                    elif p < o:
                        if p+12 == o:
                            continue
                        p += 12
                    chord = []
                    chord.append(n)
                    chord.append(o)
                    chord.append(p)
                    chords.append(deepcopy(chord))
                    for q in self.scale.notes:
                        if q == p or q == o or q == n:
                            continue
                        elif q < p:
                            if q+12 == p:
                                continue
                            q += 12
                        chord = []
                        chord.append(n)
                        chord.append(o)
                        chord.append(p)
                        chord.append(q)
                        chords.append(deepcopy(chord))
        self.chords = []
        self.chordNames = []
        for ch in chords:
            chord = []
            for n in ch:
                nname = self.scale.getNameFromNote(n)
                chord.append(nname)
            name = self._shuffle(chord)
            if len(name) > 0:
                self.chords.append(ch)
                self.chordNames.append(name)

                                           
    @classmethod
    def getNoteFromName(self,key):
        index = -1
        flat = False
        try:
            index = note_names.index(key)
        except ValueError:
            index = -1
            try:
                index = note_names2.index(key)
                flat = True
            except ValueError:
                index = -1
        return index,flat
        
    @classmethod
    def getScaleFromString(self,scale_str):
        key,stype = scale_str.split()
        note,flat = self.getNoteFromName(key)
        if note < 0 and note > 11:
            print "wrong note %s, set to c" % key
            note = 0
        sctype = Scale.major
        if stype == "major":
            sctype = Scale.major
        elif stype == "minor":
            sctype = Scale.minor
        elif stype == "minorExt":
            sctype = Scale.minorExt
        elif stype == "dorian":
            sctype = Scale.dorian
        elif stype == "lydian":
            sctype = Scale.lydian
        elif stype == "locrian":
            sctype = Scale.locrian
        elif stype == "mixolydian":
            sctype = Scale.mixolydian
        elif stype == "phrygian":
            sctype = Scale.phrygian
        elif stype == "aeolian":
            sctype = Scale.aeolian
        elif stype == "pentatonic":
            sctype = Scale.pentatonic
        elif stype == "blues":
            sctype = Scale.blues
        elif stype == "bluesMin":
            sctype = Scale.bluesMin
        elif stype == "japanese":
            sctype = Scale.japanese
        elif stype == "twelve-tone":
            sctype = Scale.twelvetone
        elif stype == "dim":
            sctype = Scale.dim
        elif stype == "aug":
            sctype = Scale.aug
        elif stype == "augmaj":
            sctype = Scale.augmaj
        else:
            print "I don't know %s, set to major" % stype
        return note,sctype,flat

    @classmethod
    def getStringFromScale(self,key,stype,flat=False):
        note = Scale.getNoteName(key,flat)
        sctype = "major"
        if stype == Scale.major:
            sctype = "major"
        elif stype == Scale.minor:
            sctype = "minor"
        elif stype == Scale.minorExt:
            sctype = "minorExt"
        elif stype == Scale.dorian:
            sctype = "dorian"
        elif stype == Scale.lydian:
            sctype = "lydian"
        elif stype == Scale.locrian:
            sctype = "locrian"
        elif stype == Scale.mixolydian:
            sctype = "mixolydian"
        elif stype == Scale.phrygian:
            sctype = "phrygian"
        elif stype == Scale.aeolian:
            sctype = "aeolian"
        elif stype == Scale.pentatonic:
            sctype = "pentatonic"
        elif stype == Scale.blues:
            sctype = "blues"
        elif stype == Scale.bluesMin:
            sctype = "bluesMin"
        elif stype == Scale.japanese:
            sctype = "japanese"
        elif stype == Scale.twelvetone:
            sctype = "twelve-tone"
        elif stype == Scale.dim:
            sctype = "dim"
        elif stype == Scale.aug:
            sctype = "aug"
        elif stype == Scale.augmaj:
            sctype = "augmaj"
        else:
            print "I don't know %s, set to major" % stype
        ret = note
        ret += " "
        ret += sctype
        return ret

    def getChordInfo(self,notes):
        if len(notes) < 3:
            print "Chord must have at least 3 notes"
            return
        self.name = notes[0]
        name = self.name
        tonic,flat = self.getNoteFromName(self.name)
        step1,flat =  self.getNoteFromName(notes[1])
        step2,flat = self.getNoteFromName(notes[2])
        
        while step1 < tonic:
            step1 += 12   
               
        while step2 < step1:
            step2 += 12      
        interval1 = step1 - tonic
        interval2 = step2 - tonic
        interval3 = -1
        if len(notes) > 3:
            step3,flat = self.getNoteFromName(notes[3])
            while step3 < step2:
                step3 += 12      

            interval3 = step3 -tonic
        #print 0,interval1,interval2,interval3
        
        if interval3 == -1: # triad
            if interval1 == 4: # major
                if interval2 == 7:
                    return name
                elif interval2 == 8:
                    name += "+"
            elif interval1 == 2:
                if interval2 == 7:
                    name +="sus2"
            elif interval1 == 3:
                if interval2 == 7:
                    name +="m"
                elif interval2 == 6:
                    name +="dim"
            elif interval1 == 5: 
                if interval2 == 7:
                    name+"sus4"
            elif interval1 == 7: 
                if interval2 == 12:
                    name += "5" #powerchord
        else:
            if interval1 == 4: #major:
                if interval2 == 7: #pure major
                    if interval3 == 10:
                        name += "7"
                    elif interval3 == 11:
                        name += "maj7"
                    elif interval3 == 9:
                        name +="6"
                    elif interval3 == 14:   
                        name +="add9"
                    elif interval3 == 8:   
                        name +="b13"
                    elif interval3 == 17:   
                        name +="add11"
                elif interval2 == 6:
                    if interval3 == 10:
                        name += "7/5-"
                    elif interval3 == 11:
                        name += "maj7/5-"
                    elif interval3 == 8:   
                        name +="7b13/5-"
                elif interval2 == 8:
                    if interval3 == 10:
                        name += "7/5+"
                    elif interval3 == 11:
                        name += "maj7/5+"
                    elif interval3 == 9:
                        name +="6/5+"
                elif interval2 == 9:
                    if interval3 == 14:
                        name += "6/9"
            elif interval1 == 3: #minor or dim         
                if interval2 == 7: #pure minor
                    if interval3 == 10:
                        name += "m7"
                    elif interval3 == 11:
                        name += "mmaj7"
                    elif interval3 == 9:
                        name +="m6"
                    elif interval3 == 14:   
                        name +="madd9"
                    elif interval3 == 8:   
                        name +="mb13"
                    elif interval3 == 17:   
                        name +="madd11"
                elif interval2 == 6: # dim
                    if interval3 == 9:   
                        name +="dim7"
            elif interval1 == 5: #sus4         
                if interval2 == 7: 
                    if interval3 == 10:
                        name += "7sus4"
                    elif interval3 == 11:
                        name += "maj7sus4"
                    elif interval3 == 9:
                        name +="6sus4"
                    elif interval3 == 14:   
                        name +="add9sus4"
                    elif interval3 == 8:   
                        name +="b13sus4"
                    elif interval3 == 17:   
                        name +="add11sus4"
            elif interval1 == 2: #sus2         
                if interval2 == 7: 
                    if interval3 == 10:
                        name += "7sus2"
                    elif interval3 == 11:
                        name += "maj7sus2"
                    elif interval3 == 9:
                        name +="6sus2"
                    elif interval3 == 14:   
                        name +="add9sus2"
                    elif interval3 == 8:   
                        name +="b13sus2"
                    elif interval3 == 17:   
                        name +="add11sus2"
        #print 0,interval1,interval2,interval3
        if name == notes[0]:
            name = ""            
        return name


    def _shuffle(self,notes):
        chordname = ""
        if len(notes) > 1:
            shuffle = []
            for n in notes:
                shuffle.append(n)
                
            steps = len(shuffle) -1
            step = 0    
            while step <= steps:
                lastname = chordname
                chordname += self.getChordInfo(shuffle)
                if len(chordname) != len(lastname):
                    chordname += ", "
                c = steps-1
                tmp = shuffle[steps]
                tmp1 = ""
                shuffle[steps] = shuffle[0]
                while c >= 0:
                    if len(tmp):
                        tmp1 = shuffle[c]
                        shuffle[c] = tmp
                        tmp = ""
                    else:    
                        tmp = shuffle[c]
                        shuffle[c] = tmp1
                        tmp1 = ""
                    c -= 1
                                    
                step += 1
        return chordname



class ChordProgressions(object):
    #progressions = [0,0,0,0,0,0,2,2,3,3,3,3,4,4,4,4,4,4,5,5] # this works only for scales with 7 notes!

    major = [0,0,0,1,2,3,3,4,4,5]
    minor = [0,0,0,2,3,3,4,4,5,6]
    minorExt = [0,0,0,1,2,3,3,4,4,5,8]
    dorian = [0,0,0,1,2,3,4,4,6]
    lydian = [0,0,0,1,2,4,4,5,6]
    mixolydian = [0,0,0,1,3,4,4,5,6]
    aeolian = [0,0,0,2,3,3,4,4,5,6]
    phrygian = [0,0,0,1,2,3,5,6]
    locrian = [0,1,2,3,4,5,6]
    blues = [0,0,0,1,4,5,5]
    bluesMin = [0,0,0,1,1,2,2,5,5]
    twelvetone = [0,1,2,3,4,5,6,7,8,9,10,11]
    aug = [0,0,0,1,3,3,5,5,6] 
    dim = [0,0,0,1,3,3,5,5,6] 
    augmaj = [0,0,0,1,2,3,3,5,5] 

    reference = { id(Scale.major): major,id(Scale.minor) : minor,id(Scale.minorExt) : minorExt, id(Scale.dorian) : dorian, id(Scale.lydian) : lydian, id(Scale.mixolydian) : mixolydian,id(Scale.aeolian) : aeolian,id(Scale.phrygian) : phrygian,id(Scale.locrian) : locrian,id(Scale.blues) : blues,id(Scale.bluesMin): bluesMin,id(Scale.twelvetone) : twelvetone,id(Scale.dim) : dim, id(Scale.aug) : aug, id(Scale.augmaj) : augmaj}



    def __init__(self,scale,beats= 2,close= False):
        self.bars = 8
        self.scale = scale # scale object
        self.close = close
        self.notes = 3
        self.beats = int(beats)

    def getRandomChord(self,chords):
        bar = random.randint(0,len(chords)-1)
        chordlist = chords[bar]
        x = random.randint(0,len(chordlist)-1)
        chord = chordlist[x]
        out = "<"
        for note in chord:
            out += note
            out += " "
        out += ">"
        return out
                   
    def getLilypondChord(self,chnote):
        chord = "<"
        offset = 0
        i = 0
        note,flat = ScaleUtil.getNoteFromName(chnote)
        note = self.scale.find(note)
        while i < self.notes:
            if i > 0:
                chord += " "
                offset += 2
                #print "chord %d, offset %d" % (chord,offset)
                if note + offset >= len(self.scale.notes):
                    offset = (note + offset) - len(self.scale.notes)
                    offset = offset - note
                #print "chord %d, offset %d after adjust octave" % (chord,offset)
                step = self.scale.notes[note + offset]
                root = self.scale.notes[note]
                #print "root %d, step %d" % (root,step)
                if root <= step:
                    step = step - root
                else:
                    step = step + 12 - root
                #print "step %d after sub" % (step)
                if step > 0:
                    if step == 3 or step == 4:
                        pass
                    elif step == 7:
                        pass
                    elif step < 3:
                        offset += 1
                    elif step > 7:
                        offset -= 1
                                
            chord += self.scale.getNameFromNote(self.scale.get(note+offset))
            i += 1
        chord += ">"
        return chord
            
 
    # generate random chord progressions
    def generate(self):
        chords = ""
        progressions = self.reference[id(self.scale.scale_type)]
        bar = 0
        while bar < self.bars:
            beats = self.beats
            out = ""
            while beats > 0:
                chord = 0 # I
                if bar > 0 and bar < self.bars-1:
                    if self.close == True:  # closing cadence I-IV-V-I
                        if bar == self.bars-3:
                            chord = 3 # IV
                        elif bar == self.bars-2:
                            chord = 4 # V
                        elif bar == self.bars-4:
                            chord = 0 # I
                        else:
                            i = random.randint(0,len(progressions)-1)
                            chord = progressions[i]
                    else:
                        i = random.randint(0,len(progressions)-1)
                        chord = progressions[i]
                note = 0
                offset = 0
                if beats < self.beats and not out.endswith(","):
                    out += ";"

                while note < self.notes:
                    if len(out) > 0 and not out.endswith(";"):
                        out += ","
                        offset += 2
                        #print "chord %d, offset %d" % (chord,offset)
                        if chord + offset >= len(self.scale.notes):
                            offset = (chord + offset) - len(self.scale.notes)
                            offset = offset - chord
                        #print "chord %d, offset %d after adjust octave" % (chord,offset)
                        step = self.scale.notes[chord + offset]
                        root = self.scale.notes[chord]
                        #print "root %d, step %d" % (root,step)
                        if root <= step:
                            step = step - root
                        else:
                            step = step + 12 - root
                        #print "step %d after sub" % (step)
                        if step > 0:
                            if step == 3 or step == 4:
                                pass
                            elif step == 7:
                                pass
                            elif step < 3:
                                offset += 1
                            elif step > 7:
                                offset -= 1
                                


                                
                    out += self.scale.getNameFromNote(self.scale.get(chord+offset))
                    note += 1
                beats -= 1
            chords += out
            chords += "|"
            bar += 1
        return chords
                
                

def usage():
        print "ScaleUtil" 
        print "usage: ScaleUtil.py [options]"
        print "-h print help"
        print "-k the key and the type of the scale, e.g. c major"
        

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hk:", ["help","key="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    key = "c major"
    for o, a in opts:
        if o in ("-k", "--key"):
            key = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
    

    seq = ScaleUtil()
    seq.setKey(key)
    print seq.getChords()
    scale = seq.scale
    prog = ChordProgressions(scale)
    print "Random chord progressions:"
    print prog.generate()


if __name__ == "__main__":
    main()
