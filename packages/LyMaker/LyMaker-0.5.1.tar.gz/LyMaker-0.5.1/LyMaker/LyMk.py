'''
LyMaker lib
@author: Acoustic E
'''
import sys,os,random
import xmlreader,ScaleUtil
from HarmonyMaker import HarmonyMaker
from GrooveMaker import GrooveMaker
from DrumMaker import DrumMaker
from MelodyMaker import MelodyMaker
from Utils import Utils
from ScaleUtil import ChordProgressions,ScaleUtil,Scale
from copy import deepcopy

VERSION = "0.5.1"
instances = [ 'I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XiV','XV','XVI','XVII','XVIII','XIX','XX','XXI','XXII','XXIII','XXIV','XXV','XXVI','XXVII','XXVIII','XXIX','XXX','XXXI','XXXII','XXXIII','XXXIV','XXXV','XXXVI','XXXVII','XXXVIII','XXXIX','XXXX']


#
#
# LYMAKER
# main class
#
#

class LyMaker(object):

    notepool = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
    notepool_alt = ['c','des','d','es','e','f','ges','g','as','a','bes','b']

    def __init__(self,name,quarters=4,beats=[],onbeat =False):
        self.chord = []
        self.chord.append("c")
        self.chord.append("e")
        self.chord.append("g")
        self.chord2 = []
        self.chord2.append("c")
        self.chord2.append("e")
        self.chord2.append("g")
        self.denominator = 4
        self.quarters = quarters
        self.eighths = quarters*2
        if not len(beats):
            self.downbeats = self._downbeats()
        else:
            self.downbeats = beats
        self.onbeat = onbeat # true = bass and drums only on pulse beats
        self.meter = "moderato"
        self.tempo = 100
        self.key = "c \\major"
        self.BbKey = "d \\major"
        self.name = name
        self.modal = False # true = do not use chord root of tonic chord in bass
        self.lasttempo = 0
        self.riffs = []
        self.harmoniesStaff = 0 # bass staff
        self.synthMode = 0 # 0= sax,trumpet & piano
        self.drumsAsInstr = 0 # 1 = drums as separate instruments

    def getBeats(self):
        return self.downbeats

    def getQuarters(self):
        return self.quarters

    def getChord(self):
        return self.chord

    def isModal(self):
        return self.modal
    
    def setSynthMode(self,mode):
        self.synthMode = mode

    def setDrumsAsInstr(self,mode):
        self.drumsAsInstr = mode

    def setKey(self,key):
        key =key.strip()
        idx = key.rfind(" ")
        k = ""
        if idx > -1:
            k = key[:idx+1]
            k += "\\"
            k += key[idx+1:]
            if key[idx+1:] == "major" or key[idx+1:] == "minor":
                self.modal = False
            else:
                self.modal = True    
        flat = False
        self.key = k    
        try:
            idx2 = self.notepool.index(key[:idx])
        except:
            idx2 = self.notepool_alt.index(key[:idx])
            flat = True
        if idx2+2 < len(self.notepool)-1:
            if flat == True:
                k = self.notepool_alt[idx2+2]
            else:
                k = self.notepool[idx2+2]
        else:
            idx2 = idx2+2  - len(self.notepool)
            if flat == True:
                k = self.notepool_alt[idx2]
            else:
                k = self.notepool[idx2]
        k += " \\"
        k += key[idx+1:]
        self.BbKey = k
      
    # set numerator for x/4 time pieces
    def setQuarters(self,quarters):
        if (quarters > 1 and quarters < 13) or quarters == 16:
            self.quarters = quarters
            self.denominator = 4
            self.setDownbeats(self._downbeats())
            self.eighths = quarters * 2
        else:
            print "%d is not a valid value for quarters" % quarters

    # set numerator for x/8 time pieces
    def setEighths(self,eighths):
        if eighths > 2 and eighths < 13:
            self.eighths = eighths
            self.denominator = 8
            self.setDownbeats(self._downbeats())
        else:
            print "%d is not a valid value for eighths" % eighths

    def setOnbeat(self,onbeat):
        self.onbeat = onbeat

    def showChords(self,key):
        sc = ScaleUtil()
        sc.setKey(key)
        return sc.getChords()
        
    def printProgressions(self,key):
        sc = ScaleUtil()
        sc.setKey(key)
        scale = sc.scale
        prog = ChordProgressions(scale)
        pp = "Random chord progressions:"
        pp += prog.generate()
        return pp

        
        
    def setTempo(self,tempo):
        self.tempo = tempo
        self._tempo2meter()

    def _tempo2meter(self):
        self.meter = "moderato"
        if self.tempo < 20:
            self.meter = "Larghissimo"
        elif self.tempo < 40:
            self.meter = "Grave"
        elif self.tempo < 45:
            self.meter = "Lento"
        elif self.tempo < 50:
            self.meter = "Largo"
        elif self.tempo < 55:
            self.meter = "Larghetto"
        elif self.tempo < 65:
            self.meter = "Adagio"
        elif self.tempo < 70:
            self.meter = "Adagietto"
        elif self.tempo < 73:
            self.meter = "Andante moderato"
        elif self.tempo < 78:
            self.meter = "Andante"
        elif self.tempo < 84:
            self.meter = "Andantino"
        elif self.tempo < 86:
            self.meter = "Marcia moderato"
        elif self.tempo < 98:
            self.meter = "Moderato"
        elif self.tempo < 110:
            self.meter = "Allegretto"
        elif self.tempo < 133:
            self.meter = "Allegro"
        elif self.tempo < 141:
            self.meter = "Vivace"
        elif self.tempo < 151:
            self.meter = "Vivacissimo"
        elif self.tempo < 168:
            self.meter = "Allegrissimo"
        elif self.tempo < 178:
            self.meter = "Presto"
        else:
            self.meter = "Prestissimo"

    # for unit tests
    def asXml(self,bassmode = 0,drummode = 0,odd = False,harmonymode = 0,randomProgressions= False,melodymode = 0,percussion = 99,feel= 0,percbeat = 0):
        text = "<LyMk>\n"
        text += "<version>%s</version>\n" % VERSION
        text += "<song>\n<name>%s</name>\n" % self.name
        numerator = 4
        if self.denominator == 4:
            numerator = self.quarters
        else:
            numerator = self.eighths
        text += "<time>%d,%d</time>\n" % (numerator,self.denominator)
        tmp = self.key.replace('\\','')
        text += "<key>%s</key>\n" % tmp
        text += "<tempo>%d</tempo>\n" % self.tempo
        text += "<structure>ABAB</structure>\n"
        beats = self.getDownbeats()
        text += "<downbeats>"
        beat = ""
        for b in beats:
           if len(beat) > 0 :
               beat += ","
           beat += "%d" % b
        text += beat   
        text += "</downbeats>\n"
        on = 0
        if self.onbeat == True:
            on = 1
        text += "<onbeat>%d</onbeat>\n" % on
        text += "<harmoniesStaff>%d</harmoniesStaff>\n" % self.harmoniesStaff
        text += "<synthMode>%d</synthMode>\n" % self.synthMode
        text += "<drumsAsInstr>%d</drumsAsInstr>\n" % self.drumsAsInstr
        text += "<part>\n"
        text += "<partname>Verse</partname>\n"
        text += "<!-- <ptempo>%d</ptempo>\n-->\n" % self.tempo
        text += "<progressions>"
        if odd == True:
            text += "c,e,g|c,e,g|a,c,e|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c,e"
        elif self.key.startswith("bes"):
            text += ""
        else: 
            text += "c,e,g|c,e,g;a,c,e,g;c,e,g|a,c,e,d|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c|f,a,c,e"
        text += "</progressions>\n"
        text += "<groove>%d</groove>\n" % bassmode
        text += "<drummode>%d</drummode>\n" % drummode
        text += "<poly>%d</poly>\n" % feel
        text += "<harmony>%d</harmony>\n" % harmonymode
        text += "<melody>%d</melody>\n" % melodymode
        text += "<percussion>%d</percussion>\n" % percussion 
        text += "<percbeat>%d</percbeat>\n" % percbeat 
        text += "</part>\n"
        text += "<part>\n"
        text += "<partname>Chorus</partname>\n"
        text += "<!-- <ptempo>%d</ptempo>\n-->\n" % self.tempo
        text += "<progressions>"
        if randomProgressions == True:
            text += ""
        elif bassmode > 0 or drummode > 0:
            text += "c,e,g|c,e,g|a,c,e|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c|f,a,c,g"
        text += "</progressions>\n"
        text += "<groove>%d</groove>\n" % bassmode
        text += "<drummode>%d</drummode>\n" % drummode
        text += "<poly>%d</poly>\n" % feel
        text += "<harmony>%d</harmony>\n" % harmonymode
        text += "<melody>%d</melody>\n" % melodymode
        text += "<percussion>%d</percussion>\n" % percussion 
        text += "<percbeat>%d</percbeat>\n" % percbeat 
        text += "</part>\n"
        text += "</song>\n"
        text += "</LyMk>"
        return text


    # for update
    def getXmlFromReader(self,reader):
        text = "<LyMk>\n"
        text += "<version>%s</version>\n" % VERSION
        text += "<song>\n<name>%s</name>\n" % self.name
        numerator = 4
        if self.denominator == 4:
            numerator = self.quarters
        else:
            numerator = self.eighths
        text += "<time>%d,%d</time>\n" % (numerator,self.denominator)
        tmp = self.key.replace('\\','')
        text += "<key>%s</key>\n" % tmp
        text += "<tempo>%d</tempo>\n" % self.tempo
        text += "<structure>%s</structure>\n" % reader.getStructure()
        beats = self.getDownbeats()
        text += "<downbeats>"
        beat = ""
        for b in beats:
           if len(beat) > 0 :
               beat += ","
           beat += "%d" % b
        text += beat   
        text += "</downbeats>\n"
        on = 0
        if self.onbeat == True:
            on = 1
        text += "<onbeat>%d</onbeat>\n" % on
        text += "<harmoniesStaff>%d</harmoniesStaff>\n" % self.harmoniesStaff
        text += "<synthMode>%d</synthMode>\n" % self.synthMode
        text += "<drumsAsInstr>%d</drumsAsInstr>\n" % self.drumsAsInstr
        i = 0
        count = reader.getPartCount()
        while i < count:
            part = reader.getPart(i)
            progressions = ""
            chords = part.progressions
            for bar in chords:
                onebar = ""
                for chord in bar:
                    if onebar != "":
                        onebar += ";"
                    chordstr = ""
                    for note in chord:
                        if chordstr != "":
                            chordstr += ","
                        chordstr += note
                    onebar += chordstr
                if progressions != "":
                    progressions += "|"
                progressions += onebar
            text += "<part>\n"
            text += "<partname>%s</partname>\n" % part.name
            if part.tempo != self.tempo and part.tempo > 0:
                text += "<ptempo>%d</ptempo>\n" % part.tempo
            text += "<progressions>"
            text += progressions
            text += "</progressions>\n"
            text += "<groove>%d</groove>\n" % part.groove
            text += "<drummode>%d</drummode>\n" % part.drummode
            text += "<poly>%d</poly>\n" % part.poly
            text += "<harmony>%d</harmony>\n" % part.harmony
            text += "<melody>%d</melody>\n" % part.melody
            text += "<percussion>%d</percussion>\n" % part.percussion 
            text += "<percbeat>%d</percbeat>\n" % part.percbeat 
            text += "</part>\n"
            i += 1
        text += "</song>\n"
        text += "</LyMk>"
        return text


    def template(self):
        template_chords =  "c,e,g|c,e,g|a,c,e|a,c,e|c,e,g|f,a,c|g,b,d|c,e,g"
        text = "<LyMk>\n"
        text += "<version>%s</version>\n" % VERSION
        text += "<song>\n<name>%s</name>\n" % self.name
        numerator = 4
        if self.denominator == 4:
            numerator = self.quarters
        else:
            numerator = self.eighths
        text += "<time>%d,%d</time>\n" % (numerator,self.denominator)
        tmp = self.key.replace('\\','')
        text += "<key>%s</key>\n" % tmp
        text += "<tempo>%d</tempo>\n" % self.tempo
        text += "<structure>ABCBCDBC</structure>\n"
        beats = self.getDownbeats()
        text += "<downbeats>"
        beat = ""
        for b in beats:
           if len(beat) > 0 :
               beat += ","
           beat += "%d" % b
        text += beat   
        text += "</downbeats>\n"
        on = 0
        if self.onbeat == True:
            on = 1
        text += "<onbeat>%d</onbeat>\n" % on
        text += "<harmoniesStaff>%d</harmoniesStaff>\n" % self.harmoniesStaff
        text += "<synthMode>%d</synthMode>\n" % self.synthMode
        #text += "<drumsAsInstr>%d</drumsAsInstr>\n" % self.drumsAsInstr
        text += "<part>\n"
        text += "<partname>Intro</partname>\n"
        text += "<!-- <ptempo>%d</ptempo>\n-->\n" % self.tempo
        text += "<progressions>"
        text += "c,e,g|a,c,e|e,g,b|f,a,c;g,b,d"
        text += "</progressions>\n"
        text += "<groove>99</groove>\n" 
        text += "<drummode>99</drummode>\n"
        text += "<poly>0</poly>\n"
        text += "<harmony>0</harmony>\n"
        text += "<melody>0</melody>\n" 
        text += "<percussion>99</percussion>\n" 
        text += "<percbeat>0</percbeat>\n"  
        text += "</part>\n"
        text += "<part>\n"
        text += "<partname>Verse</partname>\n"
        text += "<!-- <ptempo>%d</ptempo>\n-->\n" % self.tempo
        text += "<progressions>"
        text += template_chords
        text += "</progressions>\n"
        text += "<groove>2</groove>\n" 
        text += "<drummode>0</drummode>\n" 
        text += "<poly>0</poly>\n"
        text += "<harmony>0</harmony>\n"
        text += "<melody>0</melody>\n"  
        text += "<percussion>99</percussion>\n" 
        text += "<percbeat>0</percbeat>\n"  
        text += "</part>\n"
        text += "<part>\n"
        text += "<partname>Chorus</partname>\n"
        text += "<!-- <ptempo>%d</ptempo>\n-->\n" % self.tempo
        text += "<progressions>"
        text += template_chords
        text += "</progressions>\n"
        text += "<groove>2</groove>\n" 
        text += "<drummode>1</drummode>\n"
        text += "<poly>0</poly>\n"
        text += "<harmony>0</harmony>\n"
        text += "<melody>0</melody>\n" 
        text += "<percussion>99</percussion>\n" 
        text += "<percbeat>0</percbeat>\n"  
        text += "</part>\n"
        text += "<part>\n"
        text += "<partname>Bridge</partname>\n"
        text += "<!-- <ptempo>%d</ptempo>\n-->\n" % self.tempo
        text += "<progressions>"
        text += "e,g,b|e,g,b|a,c,e|a,c,e|d,f,a|d,f,a|g,b,d|g,b,d"
        text += "</progressions>\n"
        text += "<groove>5</groove>\n" 
        text += "<drummode>1</drummode>\n" 
        text += "<poly>0</poly>\n"  
        text += "<harmony>0</harmony>\n"
        text += "<melody>0</melody>\n"  
        text += "<percussion>99</percussion>\n" 
        text += "<percbeat>0</percbeat>\n"  
        text += "</part>\n"
        text += "</song>\n"
        text += "</LyMk>"
        return text


    def _downbeats(self):
        beats = [0,32]
        if self.denominator == 4:
            if self.quarters < 4:
                beats = [0] # simple duple or triple
            elif self.quarters < 6:
                beats = [0,32] # 2-2 or 2-3
            elif self.quarters == 6:
                beats = [0,48] # 3-3 compound duple
            elif self.quarters == 7:
                beats = [0,32,64] # 2-2-3 compound triple
            elif self.quarters == 8:
                beats = [0,32,64,96] # 2-2-2-2 compound quadruple
            elif self.quarters == 9:
                beats = [0,48,96] # 3-3-3 compound triple
            elif self.quarters == 10:
                beats = [0,32,80,112] # indian jhaptaal
            elif self.quarters == 11:
                beats = [0,48,112] # awiis
            elif self.quarters == 12:
                beats = [0,32,64,96,128,160] # indian ektaal
            elif self.quarters == 16:
                beats = [0,64,128,192] # indian teentaal
        elif self.denominator == 8:
            if self.eighths < 4:
                beats = [0]
            elif self.eighths == 4:
                beats = [0,16]
            elif self.eighths == 5:
                beats = [0,24]
            elif self.eighths == 6:
                beats = [0,24]
            elif self.eighths < 9:
                beats = [0,24]
            elif self.eighths == 9:
                beats = [0,24,48]
            elif self.eighths < 12:
                beats = [0,24,48]
            elif self.eighths == 12:
                beats = [0,24,48,72]
                
        return beats

    def setDownbeats(self,beats):
        if len(beats)  == 0:
            self.downbeats = self._downbeats()
        else:
            self.downbeats = beats

    def getDownbeats(self):
        beats = []
        for n in self.downbeats:
            b = 0
            if n == 0:
                b = 1
            else:
                if self.denominator == 4:
                    b = int(n / 16)
                elif self.denominator == 8:
                    b = int(n / 8)
                b += 1
            beats.append(b)
        return beats    


    def _generateRiff(self,chords,chordsInRiff = False):
        riff = []
        bars = 2
        i = 0
        seq = ScaleUtil()
        key = self.key
        key = key.replace("\\","")
        seq.setKey(key)
        scale = seq.scale
        prog = ChordProgressions(scale,len(self.downbeats),False)
        while i < bars:
            bar = chords[i]
            chord = bar[0]
            riffbar = ""
            mysum = 0
            eighths = self.eighths * 8
            while mysum < eighths:
                print_dur =""
                dur = 16
                note = ""
                play = 1
                if mysum in self.downbeats:
                    slot = random.randint(0,len(chord)-1)
                    note = chord[slot]
                    if chordsInRiff:
                        #note  = prog.getLilypondChord(note)
                        note = prog.getRandomChord(chords)
                    dur = 16
                else:
                    slot = random.randint(0,len(chord)-1)
                    note = chord[slot]
                    if chordsInRiff:
                        #note  = prog.getLilypondChord(note)
                        note = prog.getRandomChord(chords)
                    play = random.randint(0,1)
                    if mysum+16 > eighths:
                        slot = 0
                    else:    
                        slot = random.randint(0,1)
                    if slot:
                        dur = 16
                    else:
                        dur = 8    
                print_dur = Utils.findDuration(dur)
                if play == 0:
                    note = "r"
                riffbar += note
                riffbar += print_dur
                riffbar += " " 
                mysum += dur    
            riff.append(riffbar)
            i += 1
        self.riffs.append(riff)
        return 


    def _addIntro(self):
        text = '\\version "2.12.3"\n\\header {\n title = "%s"\n  composer = "LyMaker"\n  meter = "%s"\n}\n\n' % (self.name,self.meter)
        tmp = self.key.replace('\\','')        
        lily = self._isLilypondScaleType(tmp)
        key = self.key
        if lily == False:
            print "Scale %s not supported by lilypond, set to c major" % tmp
            key =  "c \\major"

        if self.denominator == 4:
            text += 'global = { \\time %d/4 }\nKey = { \\key %s }\n\n' % (self.quarters,key)
        else:    
            text += 'global = { \\time %d/8 }\nKey = { \\key %s }\n\n' % (self.eighths,key)
        return text

    def _addHarmonies(self,name,chords):
        text = '\n%s = {\n' % name
        hm = HarmonyMaker(self.eighths,self.downbeats,self.denominator)
        for bar in chords:
            text += hm.makeChord(bar,False)
            text += ' |\n '
        text += "\n}\n"
        return text

    def _addStructure(self,name):
        return "\\%s\n    " % (name)

    def _addScorePart(self,instanceCount,harmonies,perc=0):
            text = harmonies
            if self.synthMode == 0:
                text += "Trumpet = \\transpose c c' {\n\\clef treble\n\\global\n\\Key \n" 
                i = 0
                while i < instanceCount:
                    text += "\\Trumpet%s   " % instances[i]
                    i += 1
            else:
                text += "SynthOne = \\transpose c c' {\n\\clef treble\n\\global\n\\Key \n" 
                i = 0
                while i < instanceCount:
                    text += "\\SynthOne%s   " % instances[i]
                    i += 1
            text += "\n}\n"    
            text += "Right = \\transpose c c' {\n\\clef treble\n\\global\n\\Key\n" 
            i = 0
            while i < instanceCount:
                text += "\\Right%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            if self.harmoniesStaff == 0:
                text += "Left = {\n\\clef bass\n\\global\n\\Key\n"
            else:
                text += "Left = \\transpose c c' {\n\\clef treble\n\\global\n\\Key\n" 
            i = 0
            while i < instanceCount:
                text += "\\Left%s   " % instances[i]
                i +=1
            text += "\n}\n"    
            text += 'Bass = \\transpose c c, {\n\\clef "bass_8"\n\\global\n\\Key\n'
            i = 0
            while i < instanceCount:
                text += "\\Bass%s   " % instances[i]
                i += 1
            if self.drumsAsInstr == 0:    
                text += "\n}\n"    
                text += "Drums = \\drummode {\n\\global\n\\voiceOne\n"
                i = 0
                while i < instanceCount:
                    text += "\\Drums%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                text += "Cymbals = \\drummode {\n\\global\n\\voiceTwo\n"
                i = 0
                while i < instanceCount:
                    text += "\\Cymbals%s   " % instances[i]
                    i += 1
            else:
                text += "\n}\n"    
                text += "Kick =  {\n\\global\n"
                i = 0
                while i < instanceCount:
                    text += "\\Kick%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                text += "Snare =  {\n\\global\n"
                i = 0
                while i < instanceCount:
                    text += "\\Snare%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                text += "Ride =  {\n\\global\n"
                i = 0
                while i < instanceCount:
                    text += "\\Ride%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                text += "Crash =  {\n\\global\n"
                i = 0
                while i < instanceCount:
                    text += "\\Crash%s   " % instances[i]
                    i += 1
       
            text += "\n}\n"    
            if self.synthMode == 0:
                text += "PianoR = \\transpose c c'' {\n\\clef treble\n\\global\n\\Key\n"
                i = 0
                while i < instanceCount:
                    text += "\\PianoR%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                text += "PianoL = {\n\\clef bass\n\\global\n\\Key\n"
                i = 0
                while i < instanceCount:
                    text += "\\PianoL%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                tmp = self.BbKey.replace('\\','')        
                lily = self._isLilypondScaleType(tmp)
                key = self.BbKey
                if lily == False:
                    print "Scale %s not supported by lilypond, set to d major" % tmp
                    key =  "d \\major"

                text += "TenorSax = \\transpose c c' {\n\\clef treble\n\\global\n\\key %s\n\\transposition bes\n" % key
                i = 0
                while i < instanceCount:
                    text += "\\TenorSax%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
            else:
                text += "SynthThree = \\transpose c c'' {\n\\clef treble\n\\global\n\\Key\n"
                i = 0
                while i < instanceCount:
                    text += "\\SynthThree%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
                text += "SynthFour = {\n\\clef bass\n\\global\n\\Key\n"
                i = 0
                while i < instanceCount:
                    text += "\\SynthFour%s   " % instances[i]
                    i += 1
                text += "\n}\n"    

                text += "SynthTwo = \\transpose c c' {\n\\clef treble\n\\global\n\\Key\n" 
                i = 0
                while i < instanceCount:
                    text += "\\SynthTwo%s   " % instances[i]
                    i += 1
                text += "\n}\n"    
            if perc > 1 and perc != 99:
                text += "Percussion = \\transpose c c'' {\n\\clef treble\n\\global\n\\Key\n" 
            else:    
                text += "Percussion = \\drummode {\n\\global\n\n" 
            i = 0
            while i < instanceCount:
                text += "\\Percussion%s   " % instances[i]
                i += 1
            text += "\n}\n"    

            if self.synthMode == 0:
                text += '\npiano = {\n<<\n\\set PianoStaff.instrumentName = #"Piano"\n\\set PianoStaff.midiInstrument = #"acoustic grand"'
                text += '\n\\new Staff = "upper" \\PianoR\n\\new Staff = "lower" \\PianoL\n>>\n}\n'
                text += '\ntrumpet = {\n\\set Staff.instrumentName = #"Trumpet in C"\n\\set Staff.midiInstrument = #"trumpet"\n<<\n\\Trumpet\n>>\n}\n'
                text += '\ntenorSax = {\n\\set Staff.instrumentName = #"Tenor Sax"\n\\set Staff.midiInstrument = #"tenor sax"\n<<\n\\TenorSax\n>>\n}\n'
            else:
                text += '\nsynthI = {\n\\set Staff.instrumentName = #"Synth I"\n\\set Staff.midiInstrument = #"Lead 1 (square)"\n<<\n\\SynthOne\n>>\n}\n'
                text += '\nsynthII = {\n\\set Staff.instrumentName = #"Synth II"\n\\set Staff.midiInstrument = #"Lead 2 (sawtooth)"\n<<\n\\SynthTwo\n>>\n}\n'
                text += '\nsynthIII = {\n\\set Staff.instrumentName = #"Synth III"\n\\set Staff.midiInstrument = #"Pad 1 (new age)"\n<<\n\\SynthThree\n>>\n}\n'
                text += '\nsynthIV = {\n\\set Staff.instrumentName = #"Synth IV"\n\\set Staff.midiInstrument = #"Pad 2 (warm)"\n<<\n\\SynthFour\n>>\n}\n'
            text += '\nriff = {\n\\set Staff.instrumentName = #"E-Piano 1"\n\\set Staff.midiInstrument = #"electric piano 1"\n<<\n\\Right\n>>\n}\n'
            text += '\nHarmonies = {\n\\set Staff.instrumentName = #"E-Piano 2"\n\\set Staff.midiInstrument = #"electric piano 2"\n<<\n\\Left\n>>\n}\n'
            text += '\nbass = {\n\\set Staff.instrumentName = #"Bass"\n\\set Staff.midiInstrument = #"acoustic bass"\n<<\n\\Bass\n>>\n}\n'
            if self.drumsAsInstr == 0:
                text += '\ndrumContents = {\n<<\n\\set DrumStaff.instrumentName = #"Drums"\n'
                text += '\\new DrumVoice \\Cymbals\n\\new DrumVoice \\Drums\n>>\n}\n'
            else:
                text += '\nkick = {\n\\set Staff.instrumentName = #"KickDrum"\n\\set Staff.midiInstrument = #"timpani"\n<<\n\\Kick\n>>\n}\n'
                text += '\nsnare = {\n\n\\set Staff.instrumentName = #"SnareDrum"\n\\set Staff.midiInstrument = #"timpani"\n<<\n\\Snare\n>>\n}\n'
                text += '\nride = {\n\n\\set Staff.instrumentName = #"Ride"\n\\set Staff.midiInstrument = #"timpani"\n<<\n\\Ride\n>>\n}\n'
                text += '\ncrash = {\n\n\\set Staff.instrumentName = #"CrashCymbal"\n\\set Staff.midiInstrument = #"timpani"\n<<\n\\Crash\n>>\n}\n'
                

            style = "bongos"
            if perc == 1 or perc == 3:
                style = "congas"
            elif perc > 3:
                style = "percussion"

            if perc > 1 and perc != 99:
                text += '\npercussion = {\n\\set Staff.instrumentName = #"%s"\n\\set Staff.midiInstrument = #"timpani"\n<<\n\\Percussion\n>>\n}\n' % style
            else:    
                text += '\npercussion = {\n<<\n\\set DrumStaff.instrumentName = #"Percussion"\n'
                text += '\\new DrumVoice \\Percussion\n>>\n}\n'
            text += '\n\\score {\n <<\n  \\new StaffGroup\n  <<\n   '
            if self.synthMode == 0:
                text += '   \\new PianoStaff = "piano" \\piano\n'
                text += '   \\new Staff = "trumpet" \\trumpet\n'
                text += '   \\new Staff = "tenorSax" \\tenorSax\n'
            else:
                text += '   \\new Staff = "synthI" \\synthI\n'
                text += '   \\new Staff = "synthII" \\synthII\n'
                text += '   \\new Staff = "synthIII" \\synthIII\n'
                text += '   \\new Staff = "synthIV" \\synthIV\n'
            text += '   \\new Staff = "riff" \\riff\n'
            text += '   \\new Staff = "chords" \\Harmonies\n'
            text += '   \\new ChordNames {\n      \\harmonies\n   }\n'
            text += '   \\new Staff = "bass" \\bass\n'
            if self.drumsAsInstr == 0:
                text += '   \\new DrumStaff \drumContents\n'
            else:
                text += '   \\new Staff = "Kick" \\kick\n'
                text += '   \\new Staff = "Snare" \\snare\n'
                text += '   \\new Staff = "Ride" \\ride\n'
                text += '   \\new Staff = "Crash" \\crash\n'
            if perc > 1 and perc != 99 :
                text += '   \\new Staff = "%s" \\percussion\n  >>\n >>\n' % style
            else:    
                text += '   \\new DrumStaff \with { drumStyleTable = #%s-style } \percussion\n  >>\n >>\n' % style
            text += ' \\layout { }\n \\midi {\n'
            text += '   \context {\n  \\Score\n   tempoWholesPerMinute = #(ly:make-moment %d 4)\n    }\n }\n}\n' % self.tempo
            return text

    def _makeSong(self,chords):
        result = self._addIntro()
        dm = DrumMaker(self.eighths,self.downbeats,self.onbeat,5,self.denominator)
        result += dm.getPattern()
        result += "\n\n"
        if self.quarters == 4 and self.denominator == 4:
            result += dm.getDrumRoll()
            result += "\n\n"
        return result

    def _addRiffs(self):
        result = ""
        i = 65 # A
        bass = False
        for riff1,riff2 in self.riffs:
            part = chr(i)
            if bass == True:
                part += "Bass"
            result += "Riff%s = {\n %s |\n  %s |\n}\n\n" %(part,riff1,riff2)
            result += "\n\n"
            if bass == True:
                i += 1
                bass = False
            else:
                bass = True
        return result


    def _makePart(self,name,id,chords,instance,bassmode,drummode,tempo,harmonymode,melodymode,percussion,feel,percbeat):
        result = ""    
        key,type = self.key.split(" ")
        seq = ScaleUtil()
        seq.setKey(self.key.replace("\\",""))
        scale = seq.scale
        hm = HarmonyMaker(self.eighths,self.downbeats,self.denominator,harmonymode)
        gm = GrooveMaker(self.eighths,key,self.downbeats,self.onbeat,bassmode,self.isModal(),self.denominator)
        dm = DrumMaker(self.eighths,self.downbeats,self.onbeat,drummode,self.denominator,percussion,feel,percbeat,self.drumsAsInstr)
        mm = MelodyMaker(self.eighths,self.downbeats,self.denominator,scale,self.tempo,melodymode,self.synthMode)
        resultT = ""                
        resultS = ""                
        resultSR = ""                
        resultSL = ""                
        resultM = ""
        resultH = ""
        resultB = ""
        resultD = ""
        resultSD = ""
        resultC = ""
        resultCC = ""
        resultP = ""

        part = "% "
        part += "Part %s\n" % name
        if tempo == 0:
            tempo = self.tempo
        if tempo != self.lasttempo:
            part += "\\tempo 4 = %d\n" % tempo
            self.lasttempo = tempo
        
        if self.synthMode == 0:
            resultT = "Trumpet%s =  {\n" % instance
            resultT += part
            resultT += "% range from fis, to c''\n"
            resultS = "TenorSax%s =  {\n" % instance
            resultS += part
            resultS += "% range from c to f''\n"
        else:
            resultT = "SynthOne%s =  {\n" % instance
            resultT += part
            resultS = "SynthTwo%s =  {\n" % instance
            resultS += part
        resultM = "Right%s =  {\n" % instance
        resultM += part
        resultH = "Left%s = {\n" % instance
        resultH += part
        resultB = 'Bass%s = {\n' % instance 
        resultB += part
        if self.drumsAsInstr == 0:
            resultD = "Drums%s = \\drummode {\n" % instance
            resultD += part
            resultC = "Cymbals%s = \\drummode {\n" % instance
            resultC += part
        else:
            resultD = "Kick%s = {\n" % instance
            resultD += part
            resultSD = "Snare%s = {\n" % instance
            resultSD += part
            resultC = "Ride%s = {\n" % instance
            resultC += part
            resultCC = "Crash%s = {\n" % instance
            resultCC += part
        if self.synthMode == 0:
            resultSR = "PianoR%s =  {\n" % instance
            resultSR += part
            resultSL = "PianoL%s = {\n" % instance
            resultSL += part
        else:
            resultSR = "SynthThree%s =  {\n" % instance
            resultSR += part
            resultSL = "SynthFour%s = {\n" % instance
            resultSL += part
        if percussion > 1 and percussion != 99:
            resultP = "Percussion%s = {\n" % instance
        else: 
            resultP = "Percussion%s = \\drummode {\n" % instance
        resultP += part
        bars = 1
        length = len(chords)
        for bar in chords:
                barstr = "bar %d\n" % bars
                resultT += "% " + barstr
                resultS += "% " + barstr                
                savestring = ""
                if melodymode == 3 or melodymode == 2:
                    t,s = mm.process(bar)
                    resultT += t
                    resultS += s
                elif melodymode == 4:
                    s,t = mm.process(bar)
                    resultT += t
                    resultS += s
                elif melodymode == 5:
                    s,t = mm.process(bar)
                    resultS  += s
                    resultT += hm.getEmptyBar()
                    savestring = t
                elif melodymode == 6:
                    s,t = mm.process(bar)
                    resultS += hm.getEmptyBar()
                    resultT += hm.getEmptyBar()
                    savestring = s
                else:
                    s = hm.getEmptyBar()
                    t = hm.getEmptyBar()
                    resultT += t
                    resultS += s
                resultT += " | \n"
                resultS += " | \n"
                resultSR += "% " + barstr
                resultSL += "% " + barstr
                if melodymode == 1:
                    r,l = mm.process(bar)
                    resultSR += r
                    resultSL += l
                elif melodymode == 5:
                    resultSR += hm.getEmptyBar()
                    resultSL += savestring
                elif melodymode == 6:
                    if harmonymode == 6 and self.harmoniesStaff == 0: # jazz mode :-)
                        resultSL += hm.makeChord(bar,True)
                    else:
                        resultSL += hm.getEmptyBar()
                    resultSR += savestring
                else:
                    r = hm.getEmptyBar()
                    l = hm.getEmptyBar()
                    resultSR += r
                    resultSL += l
                resultSR += " | \n"
                resultSL += " | \n"
                resultM += "% " + barstr
                if harmonymode == 6 or harmonymode == 99:
                    resultM += hm.getEmptyBar()
                    resultM += " | "
                elif bars % 2 and bars < length:
                    resultM += "\Riff%s\n" % id
                elif bars % 2 and bars == length:
                    resultM += hm.getEmptyBar()
                    resultM += " | "
                else:
                    resultM + ""

                resultM += "\n"
                resultH += "% " + barstr                
                if melodymode == 6 and harmonymode == 6 and self.harmoniesStaff == 0:
                    resultH += hm.getEmptyBar()
                elif harmonymode == 99 or harmonymode == 7:
                    resultH += hm.getEmptyBar()
                else:
                    resultH += hm.makeChord(bar,True)    
                resultH += " | \n"
                if bassmode != 5:
                    resultB += "% " + barstr                
                    resultB += gm.process(bar)
                    resultB += " | \n"
                else:    
                    resultB += "% " + barstr
                    if bars % 2 and bars < length:
                        resultB += "\Riff%sBass\n" % id
                    elif bars % 2 and bars == length:
                        resultB += hm.getEmptyBar()
                        resultB += " | "
                    else:
                        resultM + ""
                    resultB += "\n"

                if self.drumsAsInstr == 0:                    
                    resultD += "% " + barstr                
                    resultD += dm.process()
                    resultD += " | \n"
                    resultC += "% " + barstr                
                    resultC += dm.getCymbals()
                    resultC += " | \n"
                else:
                    resultD += "% " + barstr                
                    resultD += dm.getKick()
                    resultD += " | \n"
                    resultSD += "% " + barstr                
                    resultSD += dm.getSnare()
                    resultSD += " | \n"
                    resultC += "% " + barstr                
                    resultC += dm.getRide()
                    resultC += " | \n"
                    resultCC += "% " + barstr                
                    resultCC += dm.getCrash()
                    resultCC += " | \n"
                resultP += "% " + barstr                
                resultP += dm.percussion()
                resultP += " | \n"
                bars +=1
        resultT += "}"                
        resultS += "}"                
        resultSR += "}"                
        resultSL += "}"                
        resultM += "}"
        resultH += "}"
        resultB += "}"
        resultD += "}"
        resultSD += "}"
        resultC += "}"
        resultCC += "}"
        resultP += "}"
        result += resultT
        result += "\n\n"
        result += resultS
        result += "\n\n"
        result += resultSR
        result += "\n\n"
        result += resultSL
        result += "\n\n"
        result += resultM
        result += "\n\n"
        result += resultH
        result += "\n\n"
        result += resultB
        result += "\n\n"
        result += resultD
        result += "\n\n"
        if self.drumsAsInstr == 1:
            result += resultSD
            result += "\n\n"
        result += resultC
        result += "\n\n"
        if self.drumsAsInstr == 1:
            result += resultCC
            result += "\n\n"
        result += resultP
        result += "\n\n"
        return result

    def _makeScore(self,instances,harmonies,perc=99):
        return self._addScorePart(instances,harmonies,perc)


    # generates random progressions for part
    # close = generate closing cadence
    def randomProgressions(self,close = False):
        seq = ScaleUtil()
        key = self.key
        key = key.replace("\\","")
        seq.setKey(key)
        scale = seq.scale
        prog = ChordProgressions(scale,len(self.downbeats),close)
        string = prog.generate()
        bars = []
        bars = string.split('|')
        barlist = []
        for b in bars:
            if len(b) == 0:
                break
            chordlist = []
            chords = []
            chords = b.split(';')
            for ch in chords:
                onechord = []
                chord = []
                chord = ch.split(',')
                for c in chord:
                    onechord.append(deepcopy(c))
                chordlist.append(deepcopy(onechord))
            barlist.append(deepcopy(chordlist))   
        return barlist

    def _isLast(self,structure,index):
        last = structure[len(structure)-1]
        offset = ord(last) - ord('A')
        if index == offset:
            return True
        else:
            return False

    def _isLilypondScaleType(self,key):
        note,type,flat = ScaleUtil.getScaleFromString(key)
        return Scale.isLilypondScale(type)

    # main routine
    # takes an xmlreader object as input
    # and generates lilypond code.
    def process(self,r):
        text = ""
        count = r.getPartCount()
        self.setTempo(r.getTempo())
        # check scale
        key,stype,flat = ScaleUtil.getScaleFromString(r.getKey())
        key = ScaleUtil.getStringFromScale(key,stype,flat)
        self.setKey(key)
        #lily = self._isLilypondScaleType(r.getKey())
        #if lily:
        #    self.setKey(r.getKey())
        #else:
        #    print "Scale %s not supported by lilypond, set to c major" % r.getKey()
        #    self.setKey("c major")
        self.setQuarters(r.getQuarters())
        if r.getEighths() > 0:
            self.setEighths(r.getEighths())
        self.setDownbeats(r.getDownbeats())
        self.setOnbeat(r.isOnbeat())
        self.harmoniesStaff = r.getHarmoniesStaff()
        self.synthMode = r.getSynthMode()
        self.drumsAsInstr = r.getDrumsAsInstr()                             
        structure = r.getStructure()
        close = False
        harmonies = ""
        callstring =  '\nharmonies = {\n    '
        i = 0
        while i < count:
            part = r.getPart(i)
            chords = part.progressions
            if len(chords) == 0:
                close = self._isLast(structure,i)
                chords = self.randomProgressions(close)
                part.progressions = chords
            if i == 0:
                text = self._makeSong(chords)        
            i += 1
            if len(chords) == 0:
                print "no chords generated, break"
                return ""
            harmonies += self._addHarmonies(part.name,chords)
            chordsInRiff = False
            if part.harmony == 7:
                chordsInRiff = True
            self._generateRiff(chords,chordsInRiff)
            # generate bass riff
            self._generateRiff(chords)
        text += self._addRiffs()
        i = 0
        perc = -1
        for s in structure:
            if i >= len(instances):
                print "more than %d actual parts, can't proceed" % i
                break
            if s < "A" or s > "Z" :
                print "invalid structure string, parts start with uppercase A and run on alphabetically..."
                break
            offset = ord(s) - ord('A')
            part = None
            part = r.getPart(offset)
            chords = part.progressions
            bassmode = part.groove
            drummode = part.drummode
            harmonymode = part.harmony
            melodymode = part.melody
            percussion = part.percussion
            feel = part.poly
            percbeat = part.percbeat
            if perc == -1 and percussion < 99:
                perc = percussion
            tempo = part.tempo
            instance = instances[i]
            i += 1
            text += self._makePart(part.name,s,chords,instance,bassmode,drummode,tempo,harmonymode,melodymode,percussion,feel,percbeat)
            callstring += self._addStructure(part.name)

        callstring += '}\n'
        harmonies += callstring
        text += self._makeScore(i,harmonies,perc)
        return text


