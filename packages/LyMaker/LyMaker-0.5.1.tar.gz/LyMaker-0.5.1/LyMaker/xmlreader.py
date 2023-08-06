#!/usr/bin/env python
'''
Created on 5 Jul 2012

@author: uwe
'''

import sys,getopt
import StringIO
from xml.sax import make_parser

from xml.sax.handler import ContentHandler
from copy import deepcopy

class PartXml:
    def __init__(self):
        self.name = ""
        self.drummode  = 0
        self.groove = 0
        self.melody = 0
        self.harmony = 0
        self.tempo = 0
        self.progressions = []
        self.percussion = 99
        self.poly = 0
        self.percbeat = 0
        
    def asString(self):
        part = self.name
        part+= ",%d,%d,%d,%d,%d\n" % (self.drummode,self.groove,self.melody,self.harmony,self.tempo)
        i = 1
        for bar in self.progressions:
            part += "%d: " % i
            i +=1
            for chord in bar:
                for note in chord:
                    part += note
                    part += " "
                part += "\n"
        return part
    
class XmlHandler(ContentHandler):
    def __init__(self):
        self.valid = False
        self.parts = []
        self.partno = 0
        self.element = 0
        self.part = None
        
        self.quarters = 4
        self.eighths = 0
        self.tempo = 120
        self.name = ""
        self.downbeats = []  
        self.key = "c major"
        self.structure = ""
        self.onbeat = 0 # offbeat
        self.harmoniesStaff = 0 # bass staff
        self.synthMode = 0 #0 = sax,trumpet & piano, 1 = all synths
        self.drumsAsInstr = 0 #1 = drums as separate instruments
        self.beats = [] # beats as characters
        
    def startElement(self, name, attrs):
        self.element = 0
        if name == "LyMk":
            self.valid = True
        elif name == "quarters":
            self.element = 1
        elif name == "tempo":
            self.element = 2
        elif name == "name":
            self.element = 3
        elif name == "downbeats":
            self.element = 4
        elif name == "key":
            self.element = 5
        elif name == "structure":
            self.element = 6
        elif name == "onbeat":
            self.element = 7
        elif name == "time":
            self.element = 8
        elif name == "harmoniesStaff":
            self.element = 9
        elif name == "synthMode":
            self.element = 10
        elif name == "drumsAsInstr":
            self.element = 11
        elif name=="part":
            self.partno = len(self.parts)
            self.part = PartXml()
        elif name=="partname":
            self.element=100
        elif name=="drummode":
            self.element=101
        elif name=="groove":
            self.element=102
        elif name=="melody":
            self.element=103
        elif name=="harmony":
            self.element=104
        elif name=="ptempo":
            self.element=105    
        elif name=="progressions":
            self.element=106    
        elif name=="percussion":
            self.element=107    
        elif name=="poly":
            self.element=108    
        elif name=="percbeat":
            self.element=109    
        else:
            self.element=9999
        return
    
    def characters(self, characters):
        if self.element == 1:
            self.quarters = int(characters)
        elif self.element == 2:
            self.tempo = int(characters)
        elif self.element == 3:
            self.name = characters
        elif self.element == 4:
            beats = characters.split(',')
        elif self.element == 5:
            self.key = characters
        elif self.element == 6:
            self.structure = characters
        elif self.element == 7:
            self.onbeat = int(characters)
        elif self.element == 8:
            time = characters.split(',')
            if len(time) == 2:
                if time[1] == '4':
                    self.quarters = int(time[0])
                elif time[1] == '8':
                    self.eighths = int(time[0])
        elif self.element == 9:
            self.harmoniesStaff = int(characters)
        elif self.element == 10:
            self.synthMode = int(characters)
        elif self.element == 11:
            self.drumsAsInstr = int(characters)
        elif self.element == 100:
            self.part.name = characters
        elif self.element == 101:
            self.part.drummode = int(characters)
        elif self.element == 102:
            self.part.groove = int(characters)
        elif self.element == 103:
            self.part.melody = int(characters)
        elif self.element == 104:
            self.part.harmony = int(characters)
        elif self.element == 105:
            self.part.tempo = int(characters)
        elif self.element == 106:
            bars = []
            bars = characters.split('|')
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
            self.part.progressions = barlist
        elif self.element == 107:
            self.part.percussion = int(characters)
        elif self.element == 108:
            self.part.poly = int(characters)
        elif self.element == 109:
            self.part.percbeat = int(characters)
        return
    
    def endElement(self,name):
        self.element = 0
        if name=="part":
            self.parts.append(deepcopy(self.part))
            self.part = None
        return
    
    def convertBeats(self):
        self.downbeats = []
        for b in self.beats:
            b.strip()
            if b == "":
                continue
            if self.eighths == 0:
                pos = (int(b)-1)*16
            else:
                pos = (int(b)-1)*8
            self.downbeats.append(pos)
        
class xmlreader:

    def __init__(self,fname):
        self.xmlfile = fname
        
    def importXML(self,content = ""):
        head = ""
        if len(content) > 0:
            head = content
        else:    
            f = None
            try:
                f = open(self.xmlfile,"r")
                head = f.read()
                f.close
            except Exception,exc:
                print " Cannot open xml file %s" % self.xmlfile
                return False
        return self._loadXML(head)

    def asString(self):
        song = self.ch.name
        song += ",%d,%d,%d,%s\n" % (self.ch.tempo,self.ch.key,self.ch.quarters,self.ch.structure)
        song += "Downbeats: "
        for b in self.ch.downbeats:
            song += str(b)
            song += " "
        song += "\n"    
        for p in self.ch.parts:
            song += p.asString()
        return song
    
    def _loadXML(self,head):
        self.ch=XmlHandler()
        saxparser=make_parser()
        saxparser.setContentHandler(self.ch)
        saxparser.parse(StringIO.StringIO(head))   #parse xml
        return self.ch.valid
    
    def getName(self):
        return self.ch.name
    
    def getQuarters(self):
        return self.ch.quarters

    def getEighths(self):
        return self.ch.eighths

    def getTempo(self):
        return self.ch.tempo
    
    def getDownbeats(self):
        self.ch.convertBeats()
        return self.ch.downbeats
    
    def isOnbeat(self):
        if self.ch.onbeat > 0:
            return True
        else:
            return False

    def getHarmoniesStaff(self):
        return self.ch.harmoniesStaff

    def getSynthMode(self):
        return self.ch.synthMode

    def getDrumsAsInstr(self):
        return self.ch.drumsAsInstr

    def getStructure(self):
        if self.ch.structure == "":
            print "structure is empty!"
        return self.ch.structure
    
    def getKey(self):
        return self.ch.key
    
    def getPartCount(self):
        return len(self.ch.parts)
        
    def getPart(self,index):
        if index >= len(self.ch.parts):
            print "part %d is out of range" % (index)
            return None
        else:
            return self.ch.parts[index]
            
def usage():
    print "xmlreader.py -f, f = filename"

if __name__ == '__main__':
    fname = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == "-f":
            fname = a
        if o in ("-h", "--help"):
            usage()
            sys.exit()
    if fname == "":
        usage()
        sys.exit(2)
    app = xmlreader(fname)
    app.importXML()
    print app.asString()    
