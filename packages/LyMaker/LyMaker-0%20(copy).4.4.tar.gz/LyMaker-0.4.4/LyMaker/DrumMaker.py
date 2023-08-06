import random
from Utils import Utils
#
# DRUMMAKER
# creates a drumline
#
class DrumMaker(object):


        bongos = ['boh','bol','bolo','boho','bohm','ssh','bolm','ssl','r','r','r','r']
        congas = ['cgh','cgho','cghm','ssh','cgl','cglo','cglm','ssl','r','r','r','r']

        def __init__(self,eighths,beats,onbeat = False,mode = 0,denominator = 4,percmode = 99):
            self.beats = beats
            self.eighths = eighths
            self.onbeat = onbeat
            self.denominator = denominator
            # mode 0 = bass drum, snare and (a lot of)  highhat
            # mode 1 = like 0 but with less highhat and less snare
            # mode 2 = highhat only
            # mode 3 = no bass drum
            # mode 4 = funky
            # mode 5 = pattern
            # mode 99 = no drums at all
            self.mode = mode
            self.percmode = percmode
        
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
            if self.onbeat:
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
                note = "hh"
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


        # onbeat drums
        # bass drum (bd) on downbeats
        # snare drum (sn) on upbeats
        def _straight(self):
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
                if mysum in self.beats: # downbeat
                    note = "bd"
                    if self.mode == 3:
                        play = 0
                    else:
                        play = 1
                    if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                        beat += 1
                elif (mysum % denominator) == 0: # upbeat
                    play = 1
                    note = "sn"
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


        # random offbeat percussion
        def percussion(self):
            if self.percmode == 99:
                text = ""
                i = 0
                while i < self.eighths:
                    text += " r8 "
                    i += 1    
                return text
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
            while mysum < (self.eighths * 8):
                note = ""
                x = random.randint(0,len(notes)-1)
                note = notes[x]
                result += note
                result += pdur
                result += " "
                mysum += dur
            return result
