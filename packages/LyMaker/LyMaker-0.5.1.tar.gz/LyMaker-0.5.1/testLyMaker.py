import unittest
from LyMaker import LyMk,xmlreader
import os

class testLyMaker(unittest.TestCase):
    
    filename = "testLyMaker"


    def testBasic(self):
        print ("----------------------------")
        print ("basic test with 4/4 offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test2Q(self):
        print ("----------------------------")
        print("test with 2/4 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(2)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test3Q(self):
        print ("----------------------------")
        print("test with 3/4 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(3)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test5Q(self):
        print ("----------------------------")
        print("test with 5/4 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(5)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test6Q(self):
        print ("----------------------------")
        print("test with 6/4 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(6)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test7Q(self):
        print ("----------------------------")
        print("test with 7/4 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(7)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test9Q(self):
        print ("----------------------------")
        print("test with 9/4 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(9)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testBasicOn(self):
        print ("----------------------------")
        print("test with 4/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test2QOn(self):
        print ("----------------------------")
        print("test with 2/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(2)
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test3QOn(self):
        print ("----------------------------")
        print("test with 3/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(3)
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test5QOn(self):
        print ("----------------------------")
        print("test with 5/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(5)
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test6QOn(self):
        print ("----------------------------")
        print("test with 6/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(6)
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test7QOn(self):
        print ("----------------------------")
        print("test with 7/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(7)
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def test9QOn(self):
        print ("----------------------------")
        print("test with 9/4 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(9)
        maker.setOnbeat(True)
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testStrangeDownbeats(self):
        print ("----------------------------")
        print("test with 4/4 time and downbeats 2 and 4")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(4)
        maker.setDownbeats([16,48])
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testStrangeDownbeatsII(self):
        print ("----------------------------")
        print("test with 4/4 time and downbeats 1 and 2")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(4)
        maker.setDownbeats([0,16])
        content = maker.asXml()
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testFunky(self):
        print ("----------------------------")
        print("test with 4/4 time and funky feel and bass riff")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(4)
        content = maker.asXml(5,4)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testWalking(self):
        print ("----------------------------")
        print("test with 5/4 time and walking bass and high-hat only")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(5)
        content = maker.asXml(1,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testShuffle(self):
        print ("----------------------------")
        print("test with 4/4 time and shuffle bass and drumpattern")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(4)
        content = maker.asXml(4,5)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testEmpty(self):
        print ("----------------------------")
        print("test with 9/4 time and empty bass- and drumline")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(9)
        content = maker.asXml(99,99)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testOddBars(self):
        print ("----------------------------")
        print("test with 4/4 time and odd count of bars")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(4)
        content = maker.asXml(2,1,True)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testShowChords(self):
        print ("----------------------------")
        print("test with the -s option")
        maker = LyMk.LyMaker(self.filename)
        text = maker.showChords("b minor")
        assert len(text) > 0

    def testEighths(self):
        print ("----------------------------")
        print("test with 9/8 time offbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(9)
        maker.setOnbeat(0)
        content = maker.asXml(0,0)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testEighthsOn(self):
        print ("----------------------------")
        print("test with 9/8 time onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(9)
        maker.setOnbeat(1)
        content = maker.asXml(0,0)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testOddEighths(self):
        print ("----------------------------")
        print("test with 12/8 time and odd bars")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(12)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testNoteUpQuarters(self):
        print ("----------------------------")
        print("test with 7/4 time and note-up arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,1)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testNoteUpEighths(self):
        print ("----------------------------")
        print("test with 7/8 time and note-up arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,1)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0


    def testNoteDownQuarters(self):
        print ("----------------------------")
        print("test with 7/4 time and note-down arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testNoteDownEighths(self):
        print ("----------------------------")
        print("test with 7/8 time and note-down arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testRandomQuarters(self):
        print ("----------------------------")
        print("test with 7/4 time and random arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,3)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testRandomEighths(self):
        print ("----------------------------")
        print("test with 7/8 time and random arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,3)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testBarUpDownEighths(self):
        print ("----------------------------")
        print("test with 7/8 time and note-up/note-down arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,4)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testBarDownUpEighths(self):
        print ("----------------------------")
        print("test with 7/8 time and note-down/note-up arpeggio")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(7)
        maker.setOnbeat(1)
        content = maker.asXml(1,0,True,5)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testRandomProgressions(self):
        print ("----------------------------")
        print("test with 5/4 time and random progressions")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(5)
        maker.setOnbeat(0)
        content = maker.asXml(1,0,True,0,True)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testMelody1(self):
        print ("----------------------------")
        print("test with 6/8 time and melody mode 1")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setEighths(6)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,True,0,True,1)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testMelody2(self):
        print ("----------------------------")
        print("test with 5/4 time and melody mode 2")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(5)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,True,0,True,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testMelody3(self):
        print ("----------------------------")
        print("test with 3/4 time and melody mode 3")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(3)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,True,0,True,3)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testMelody4(self):
        print ("----------------------------")
        print("test with 4/4 time and melody mode 4")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,True,0,True,4)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testMelody5(self):
        print ("----------------------------")
        print("test with 2/4 time and melody mode 5")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setQuarters(2)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,True,0,True,5)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0


    def testFlatKey(self):
        print ("----------------------------")
        print("test with 4/4 time and flat key")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("bes minor")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,False,0,True,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testPianoSoloNoRiff(self):
        print ("----------------------------")
        print("test with 4/4 time and piano solo, no riff")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,False,6,True,6)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testHarmoniesUp(self):
        print ("----------------------------")
        print("test with 4/4 time and harmonies in violin staff")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        maker.harmoniesStaff = 1
        content = maker.asXml(2,0,False,0,True,6)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testBongos(self):
        print ("----------------------------")
        print("test with 9/8 time and bongos")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setEighths(9)
        maker.setOnbeat(0)
        maker.harmoniesStaff = 0
        content = maker.asXml(2,0,False,0,True,6,0)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testCongas(self):
        print ("----------------------------")
        print("test with 3/4 time and congas")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(3)
        maker.setOnbeat(0)
        maker.harmoniesStaff = 0
        content = maker.asXml(2,0,False,0,True,6,1)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testUpdate(self):
        print ("----------------------------")
        print("test with 12/8 time and update")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setEighths(12)
        maker.setOnbeat(0)
        maker.harmoniesStaff = 0
        content = maker.asXml(2,0,True,0,True,2,0)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text,True,r,maker)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testUnsupportedScale(self):
        print ("----------------------------")
        print("test with non-Lilypond scale and random melody")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("bes dim")
        #maker.setKey("bes bluesMin")
        maker.setQuarters(5)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,False,0,True,2,0)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testSynthMode(self):
        print ("----------------------------")
        print("test with synthMode = 1")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(5)
        maker.setOnbeat(0)
        maker.setSynthMode(1)
        content = maker.asXml(2,0,False,0,True,2,0)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testPoly(self):
        print ("----------------------------")
        print("test with polyrhythms")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        content = maker.asXml(2,0,False,0,True,2,0,8,9)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testClaves(self):
        print ("----------------------------")
        print("test with bongo claves")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(1)
        content = maker.asXml(2,0,False,0,True,2,0,2,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testFunkyStraight(self):
        print ("----------------------------")
        print("test with drummode 4 onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(1)
        content = maker.asXml(2,4,False,0,True,2,0,2,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testHalftimeStraight(self):
        print ("----------------------------")
        print("test with drummode 1 onbeat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(1)
        content = maker.asXml(2,1,False,0,True,2,0,2,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testNoCh10Percussion(self):
        print ("----------------------------")
        print("test with percussion as normal instruments")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(1)
        content = maker.asXml(2,0,False,0,True,2,2,2,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testDrumsAsInstr(self):
        print ("----------------------------")
        print("test with drums as normal instruments")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        maker.setDrumsAsInstr(1)
        content = maker.asXml(2,4,False,0,True,2,2,2,2)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testBasicBongoBeat(self):
        print ("----------------------------")
        print("test with basic bongo beat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        maker.setDrumsAsInstr(1)
        content = maker.asXml(2,4,False,0,True,2,2,2,10)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testBasicCongaBeat(self):
        print ("----------------------------")
        print("test with basic conga beat")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("c major")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        maker.setDrumsAsInstr(1)
        content = maker.asXml(2,4,False,0,True,2,3,2,10)
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def testChordsInRiff(self):
        print ("----------------------------")
        print("test with chords in riff")
        maker = LyMk.LyMaker(self.filename)
        r = xmlreader.xmlreader(self.filename+ ".xml")
        maker.setKey("bes minor")
        maker.setQuarters(4)
        maker.setOnbeat(0)
        maker.setDrumsAsInstr(1)
        content = maker.asXml(2,4,False,7,True,2,3,5,10) #bass,drum,odd,harmony,random,melody,percussion,poly,percbeat
        r.importXML(content)
        text = maker.process(r)
        ok = self._write(text)
        assert ok == True
        cmd = "lilypond %s%s" % (self.filename,".ly") 
        ret = os.system(cmd)
        assert ret == 0

    def _write(self,text,update=False,r=None,maker=None):
        if len(text) == 0:
            return False
        if update == True and r and maker:
            content = maker.getXmlFromReader(r)
            r2 = xmlreader.xmlreader(self.filename+ ".xml")
            r2.importXML(content)
            text = maker.process(r2)

        outf = None
        try:
            outf = open(self.filename + ".ly","w")
        except:
            print "Cannot open %s" % (self.filename + ".ly")
            return False
        if outf:    
            outf.write(text)
            outf.flush()
            outf.close
            return True





if __name__ == "__main__":
    unittest.main() # run all tests
