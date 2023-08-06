import random
from Utils import Utils
#
# DRUMMAKER
# creates a drumline
#
class DrumMaker(object):


        bongos = ['boh','bol','r','r','r','r']
        congas = ['cgh','cgho','cgl','r','r','r','r']

        bongosNoCh10 = ['f','c','r','r','r','r'] #quint
        congasNoCh10 = ['f','f','c','r','r','r','r'] # 2 quints

        def __init__(self,eighths,beats,onbeat = False,mode = 0,denominator = 4,percmode = 99,feel = 0,percbeat = 0,drumsAsInstr = 0):
            self.beats = beats
            self.eighths = eighths
            self.onbeat = onbeat
            self.denominator = denominator
            self.drumsAsInstr = drumsAsInstr
            # mode 0 = bass drum, snare and (a lot of)  ride
            # mode 1 = like 0 but with less ride and less snare
            # mode 2 = ride only
            # mode 3 = no bass drum
            # mode 4 = funky
            # mode 5 = pattern
            # --- modes onbeat
            # mode 0 = bass drum on downbeats, snare on upbeats
            # mode 1 = halftime
            # mode 4 = funky straight
            # mode 99 = no drums at all
            self.mode = mode
            self.percmode = percmode
            # poly feel
            # 0 = random or straight
            # 1 - light swing
            # 2 - 2 over 3 eighths
            # 3 - hard swing
            # 4 - 3 over 2 quarters
            # 5 - 3 over 2 seminotes
            # 6 - 5 over 4
            # 7 - 7 over 4
            # 8 - 11 over 4
            # 9 - 13 over 4     
            # 10 = 2-3 clave
            # 11 = 3-2 clave
            self.feel = feel # swing feeling
            self.claveside = 0 # 2-side
            if feel == 11:
                self.claveside = 1 # 3-side
            # percmodes
            # 0 - bongos
            # 1 - congas
            # 2 - bongos no drum channel
            # 3 - congas no drum channel
            # percbeat
            # 0 = random
            # 1 - 2-3 clave
            # 2 - 3-2 clave
            # 3 - 3 over 2 eighths
            # 4 - 3 over 2 quarters
            # 5 - 3 over 2 seminotes
            # 6 - 5 over 4
            # 7 - 7 over 4
            # 8 - 11 over 4
            # 9 - 13 over 4     
            self.claveside2 = 0 # 2-side
            if percbeat == 2:
                self.claveside2 = 1 # 3-side
            self.percbeat = percbeat
        
        def getPattern(self):
            text = "Drumpattern = { \\drummode { "
            i = 0
            if self.denominator == 4:
                while i*2 < self.eighths:
                    if i*16 in self.beats:
                        text += "\n  bd16 r r r" # downbeat
                    else:
                        text += "\n  sn16 r r r" # upbeat
                    i += 1
            else:
                while i < self.eighths:
                    if i*8 in self.beats:
                        text += "\n  bd16 r" # downbeat
                    else:
                        text += "\n  sn16 r " # upbeat
                    i += 1    
            text += "\n             } }\n"
            return text

        def getEmptyBar(self):
            text = ""
            i = 0
            while i < self.eighths:
                text += " r8 "
                i += 1    
            return text
       
        def getDrumRoll(self):
            text = "Drumroll = { \\drummode { "
            # bar 1
            text += "\n<sn bd>16 <sn bd>8 sn16 sn8 sn8:32 ~ "
            text += "\nsn8 sn8 sn4:32 ~| "
            # bar 2
            text += "\nsn16 sn8 sn16 sn8 sn16 sn16 "
            text += "\nsn4 r4 | "
            text += "\n  }"
            text += "\n}\n"
            return text

        def getRide(self):
            text = self.getCymbals()
            text = text.replace('cymr','c')
            text = text.replace('hh','c')
            return text
            
        def getCrash(self):
            return self.getEmptyBar()

        def getKick(self):
            text = self.process()
            text = text.replace('<bd sn>','c')
            text = text.replace('bd','c')
            text = text.replace('sn','r')
            return text

        def getSnare(self):
            text = self.process()
            text = text.replace('<bd sn>','c')
            text = text.replace('bd','r')
            text = text.replace('sn','c')

            return text
    
        # random highhat
        # always play on the downbeats
        # else higher probability between downbeat and upbeat
        def getCymbals(self):
            if self.mode == 99:
                text = ""
                i = 0
                while i < self.eighths:
                    text += " r8 "
                    i += 1    
                return text
            if self.onbeat and self.feel == 0:
                return self._getCymbalsStraight()
            elif self.feel > 0 and self.feel < 4:
                return self._getCymbalsSwing()
            elif self.feel == 4 and self.eighths == 8: # polyrhythms for 4/4 only
                return self._getPoly(3,2,4)  # 3 over 2 quarters    
            elif self.feel == 5 and self.eighths == 8:
                return self._getPoly(3,2,2)  # 3 over 2 seminotes
            elif self.feel == 6 and self.eighths == 8:
                return self._getPoly(5,4,4)  # 5 over 4  
            elif self.feel == 7 and self.eighths == 8:
                return self._getPoly(7,4,4)  # 7 over 4  
            elif self.feel == 8 and self.eighths == 8:
                return self._getPoly(11,4,4)  # 11 over 4  
            elif self.feel == 9 and self.eighths == 8:
                return self._getPoly(13,4,4)  # 13 over 4  
            elif self.feel == 10 and self.eighths == 8:
                if self.claveside == 0:
                    self.claveside = 1
                    return self._clave2()
                else:
                    self.claveside = 0
                    return self._clave3()
            elif self.feel == 11 and self.eighths == 8:
                if self.claveside == 0:
                    self.claveside = 1
                    return self._clave2()
                else:
                    self.claveside = 0
                    return self._clave3()
            elif self.onbeat:
                return self._getCymbalsStraight()

            mysum = 0
            result = ""
            beat = 0
            dur = 4
            pause = 1
            upbeat_factor = 5
            downbeat_factor = 1
            if self.mode == 1:
                upbeat_factor += 5
                downbeat_factor += 4
            denominator = self.denominator
            if denominator == 4:
                denominator = 16

            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                note = "cymr"
                if mysum in self.beats: # on the downbeat
                    pause = 0
                elif mysum < self.beats[beat]+denominator: # before upbeat
                    pause = random.randint(0,downbeat_factor)
                else:
                    pause = random.randint(0,upbeat_factor)
                if pause == 0:
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
                if beat+1 < len(self.beats):
                    if mysum == self.beats[beat+1]:
                        beat += 1
            return result
        
        # highhat Charlie Watts's style
        # highhat is always played on the downbeat and between downbeat and upbeat
        # highhat is never played on the upbeat and between upbeat and downbeat
        def _getCymbalsStraight(self):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            pause = 1
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                note = "hh"
                if mysum < self.beats[beat]+denominator: # before upbeat
                    pause = 0
                else:
                    pause = 1
                if pause == 0:
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
                if beat+1 < len(self.beats):
                    if mysum == self.beats[beat+1]:
                        beat += 1
            return result

        # ride cymbal swing
        def _getCymbalsSwing(self):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            pause = 1
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                if self.feel == 1: # swing
                    note = "cymr8 r32 cymr16. "
                elif self.feel == 2: # medium - triplet
                    note = "\\times 2/3 { cymr4 cymr8 } "
                else: # hard swing
                    note = "cymr8. cymr16 "
                result += note
                mysum += 16 # one beat
                if beat+1 < len(self.beats):
                    if mysum == self.beats[beat+1]:
                        beat += 1
            return result

        # ride cymbal poly
        def _getPoly(self,notes = 3,over = 2,ndur = 4,instr=['cymr']):
            result = ""
            instrprog = []
            i = int(notes)
            while i > 0:
                if len(instr) == 1:
                    x = 0
                else:
                    x = random.randint(0,len(instr)-1)
                instrprog.append(instr[x])
                i -= 1
            if notes == 3:
                if over == 2:
                    result = "\\times 2/3 {%s%d %s%d %s%d} " % (instrprog[0],ndur,instrprog[1],ndur,instrprog[2],ndur)
                    if ndur == 4:
                        result += "\\times 2/3 {%s%d %s%d %s%d} " % (instrprog[0],ndur,instrprog[1],ndur,instrprog[2],ndur)
                    if ndur == 8:
                        result += "\\times 2/3 {%s%d %s%d %s%d} " % (instrprog[0],ndur,instrprog[1],ndur,instrprog[2],ndur)
                        result += "\\times 2/3 {%s%d %s%d %s%d} " % (instrprog[0],ndur,instrprog[1],ndur,instrprog[2],ndur)
                        result += "\\times 2/3 {%s%d %s%d %s%d} " % (instrprog[0],ndur,instrprog[1],ndur,instrprog[2],ndur)
            elif notes == 5:
                result = "\\times 4/5 {%s4 %s4 %s4 %s4 %s4} " % (instrprog[0],instrprog[1],instrprog[2],instrprog[3],instrprog[4])
            elif notes == 7:
                result = "\\times 4/7 {%s4 %s4 %s4 %s4 %s4 %s4 %s4} " % (instrprog[0],instrprog[1],instrprog[2],instrprog[3],instrprog[4],instrprog[5],instrprog[6])
            elif notes == 11:
                result = "\\times 4/11 {%s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4} " % (instrprog[0],instrprog[1],instrprog[2],instrprog[3],instrprog[4],instrprog[5],instrprog[6],instrprog[7],instrprog[8],instrprog[9],instrprog[10])
            elif notes == 13:
                result = "\\times 4/13 {%s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4 %s4} " % (instrprog[0],instrprog[1],instrprog[2],instrprog[3],instrprog[4],instrprog[5],instrprog[6],instrprog[7],instrprog[8],instrprog[9],instrprog[10],instrprog[11],instrprog[12])
            return result

        # onbeat drums
        # bass drum (bd) on downbeats
        # snare drum (sn) on upbeats
        # 0 4 8 12 16 20 24 28 32 36 40 44 48 52 56 60 64
        # d - -  - u   - -  -  d  -  -  -  u   -  - -   
        def _straight(self):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            play = 1
            toggle = 0
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                note = ""
                if mysum in self.beats: # downbeat
                    note = "bd"
                    if self.mode == 3:
                        play = 0
                    else:
                        play = 1
                    if self.mode == 4 and self.eighths == 8 and mysum == 32:
                        note = "<bd sn>"
                    elif self.mode == 1:
                        if toggle == 1:
                           note = "sn"
                           toggle = 0
                        elif toggle == 0:
                           toggle = 1     
                    if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                        beat += 1
                elif (mysum % denominator) == 0: # upbeat
                    play = 1
                    note = "sn"
                    if self.mode == 4 and self.eighths == 8 and mysum == 16:
                        play = 0
                    elif self.mode == 1:
                        play = 0    
                else:   # offbeat
                    play = 0                

                if play:
                        result += note
                        result += pdur
                        result += " "
                else:
                        result += "r"
                        result += pdur
                        result += " "
                mysum += dur

            return result

        # clave 2-part
        # ride cymbals 5 notes over 2 bars
        # 4/4 beat
        def _clave2(self,instr1 = "cymr",instr2 = "cymr"):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            play = 1
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            if (self.eighths * 8 ) != 64:
                return self._getCymbalsStraight()
            while mysum < (self.eighths * 8):
                note = ""
                if mysum == 16: # 1st upbeat
                    note = instr1
                    play = 1
                elif mysum == 32: # 2nd downbeat if 4/4
                    note = instr2
                    play = 1
                else:
                    play = 0
                if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                    beat += 1

                if play:
                        result += note
                        result += pdur
                        result += " "
                else:
                        result += "r"
                        result += pdur
                        result += " "
                mysum += dur
            return result

        # clave 3-part
        # ride cymbals 5 notes over 2 bars
        # 4/4 beat
        def _clave3(self,instr1 = "cymr",instr2 = "cymr",instr3 = "cymr"):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            play = 1
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            if (self.eighths * 8 ) != 64:
                return self._getCymbalsStraight()
            while mysum < (self.eighths * 8):
                note = ""
                if mysum == 0: # 1st downbeat
                    note = instr1
                    play = 1
                elif mysum == 24: # 
                    note = instr2
                    play = 1
                elif mysum == 48: # 
                    note = instr3
                    play = 1
                else:
                    play = 0
                if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                    beat += 1

                if play:
                        result += note
                        result += pdur
                        result += " "
                else:
                        result += "r"
                        result += pdur
                        result += " "
                mysum += dur
            return result


        # random offbeat drums
        # always bass drum on downbeats
        # random snare, random bass drum between down- and upbeats
        def process(self):
            if self.mode == 99 or self.mode == 2:
                text = ""
                i = 0
                while i < self.eighths:
                    text += " r8 "
                    i += 1    
                return text
            elif self.mode == 5:
                return "\\Drumpattern\n"
            if self.onbeat:
                return self._straight()
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            play = 1
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            while mysum < (self.eighths * 8):
                note = ""
                if mysum in self.beats: # this is a downbeat
                    note = "bd"
                    if self.mode == 3:
                        play = 0
                    else:    
                        play = 1
                    if self.mode == 4 and mysum != 0: # funky
                        note = "<bd sn>"        
                    if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                        beat += 1
                elif beat+1 < len(self.beats) and mysum == (self.beats[beat+1] - dur): # one sixteenth before next downbeat
                    play = 1
                    if self.mode == 3:
                        play = 0
                    note = "bd"
                elif mysum < (self.beats[beat] + denominator): # between downbeat and upbeat
                    prop = 3
                    if self.mode == 4:
                        prop = 2
                    donotplay = random.randint(0,prop)
                    play = 0
                    if donotplay == 0 and self.mode != 3:
                        play = 1
                    if beat == 0:
                        play = 0
                    note = "bd"
                elif mysum > self.beats[len(self.beats)-1]: # after last downbeat
                    play = random.randint(0,1)
                    note = "sn"
                elif mysum == self.beats[beat]+denominator: # this is a upbeat
                    play = 1
                    note = "sn"
                    if self.mode == 4 and beat == 0:
                        play = 0 # funky, no snare on first upbeat
                else: # between upbeat and downbeat
                    prop = 3
                    if self.mode == 0 or self.mode == 3 or self.mode == 4:
                        prop = 1
                    donotplay = random.randint(0,prop)
                    play = 0
                    if donotplay == 0:
                        play = 1
                    note = "sn"
                    if self.mode == 4 and beat == 0:
                        play = 0 # funky, no snare on first upbeat
                    

                if play:
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
            return result

        def _getBasicRhythm(self,instr = ['boh','bol']):
            if self.percmode == 0 or self.percmode == 2:        
                text = "%s8\\mf %s\\pp %s %s\\pp %s %s\\pp %s\\mf %s" % (instr[0],instr[0],instr[0],instr[0],instr[0],instr[0],instr[1],instr[0])
            else:
                text = "\\times 2/3 {%s8\\ff %s16} \\times 2/3 {r8 %s16}  \\times 2/3 {%s8 %s16} \\times 2/3 {%s8\\ff %s16\\ff}  \\times 2/3 {%s8 %s16} \\times 2/3 {r8 %s16}  \\times 2/3 {%s8 %s16} \\times 2/3 {%s8\\ff %s16\\ff}"  % (instr[2],instr[1],instr[1],instr[1],instr[1],instr[0],instr[2],instr[1],instr[1],instr[1],instr[1],instr[1],instr[0],instr[2])

            return text
    
        # random offbeat percussion
        def percussion(self):
            if self.percmode == 99:
                text = ""
                i = 0
                while i < self.eighths:
                    text += " r8 "
                    i += 1    
                return text
            if self.percbeat > 0 and (self.eighths * 8 ) == 64:
                if self.percbeat == 1 or self.percbeat == 2: # claves    
                    if self.claveside2 == 0:
                        self.claveside2 = 1
                        if self.percmode == 0:
                            return self._clave2("boh","bol")
                        elif self.percmode == 1:
                            return self._clave2("cgh","cgl")
                        elif self.percmode == 2:
                            return self._clave2("f","c")
                        elif self.percmode == 3:
                            return self._clave2("f","c")
                    else:
                        self.claveside2 = 0
                        if self.percmode == 0:
                            return self._clave3("boh","bol","bol")
                        elif self.percmode == 1:
                            return self._clave3("cgho","cgl","cgl")
                        elif self.percmode == 2:
                            return self._clave3("f","c","c")
                        elif self.percmode == 3:
                            return self._clave3("f","c","c")
                elif self.percbeat > 2:
                    instr = []    
                    if self.percmode == 0:
                        instr = ['bol','boh']
                    elif self.percmode == 2:
                        instr = ['c','f']
                    elif self.percmode == 3:
                        instr = ['c','f','f']
                    else:
                        instr = ['cgl','cgho','cgh']    
                    if self.percbeat == 3:
                        return self._getPoly(3,2,8,instr)  # 3 over 2 eighths    
                    elif self.percbeat == 4:
                        return self._getPoly(3,2,4,instr)  # 3 over 2 quarters    
                    elif self.percbeat == 5:
                        return self._getPoly(3,2,2,instr)  # 3 over 2 seminotes
                    elif self.percbeat == 6:
                        return self._getPoly(5,4,4,instr)  # 5 over 4  
                    elif self.percbeat == 7:
                        return self._getPoly(7,4,4,instr)  # 7 over 4  
                    elif self.percbeat == 8:
                        return self._getPoly(11,4,4,instr)  # 11 over 4  
                    elif self.percbeat == 9:
                        return self._getPoly(13,4,4,instr)  # 13 over 4  
                    elif self.percbeat == 10:
                        return self._getBasicRhythm(instr)  # basic bongo or conga rhythm  

            mysum = 0
            result = ""
            dur = 4
            play = 1
            denominator = self.denominator
            if denominator == 4:
                denominator = 16
            pdur = Utils.findDuration(dur)
            notes = self.bongos
            if self.percmode == 1:
                notes = self.congas
            elif self.percmode == 2:
                notes = self.bongosNoCh10
            elif self.percmode == 3:
                notes = self.congasNoCh10    
            while mysum < (self.eighths * 8):
                note = ""
                x = random.randint(0,len(notes)-1)
                note = notes[x]
                result += note
                result += pdur
                if mysum == 0 and note != 'r':
                    result += "\mf"
                result += " "
                mysum += dur
            return result
