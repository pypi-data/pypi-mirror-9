'''
LyMaker
@author: Acoustic E
'''
import sys, getopt,os
from LyMaker import LyMk,xmlreader


VERSION = "0.5.1"

def usage():
    print "LyMaker (Version %s)" % VERSION
    print "usage: LyMaker.py [options]"
    print "-h print help"
    print "-f xml filename (without extension)"
    print "-t create template xml file"
    print "-s show scale and valid chords for key, e.g. -s\"c major\""
    print "-p print random progressions for key, e.g. -p\"c major\""
    print "-u update the xml file"

#
# MAIN
# isn't it?
#
#
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htuf:s:p:", ["help","template","update","file=","show=","progressions="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    automatic = False
    template = False
    filename = "default"
    key = "c major"
    show = False
    update = False
    progressions = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            filename = a
            automatic = True
        elif o in ("-s", "--show"):
            key = a
            show = True
        elif o in ("-p", "--progressions"):
            key = a
            progressions = True
        elif o in ("-t", "--template"):
            template = True
        elif o in ("-u", "--update"):
            update = True
    mm = LyMk.LyMaker(filename)
    if automatic:
        r = xmlreader.xmlreader(filename+ ".xml")
        r.importXML()
        text = mm.process(r)
        if len(text) == 0:
            sys.exit(2)
        outf = None
        try:
            outf = open(filename + ".ly","w")
        except:
            print "Cannot open %s" % (filename + ".ly")
        if outf:    
            outf.write(text)
            outf.flush()
            outf.close
        if update:
            text = mm.getXmlFromReader(r)
            outx = None
            try:
                outx = open(filename + ".xml","w")
            except:
                print "Cannot open %s" % (filename + ".xml")
            if outx:    
                outx.write(text)
                outx.flush()
                outx.close
    elif template:
        outf = None
        try:
            outf = open("template.xml","w")
        except:
            print "Cannot open %s" % ("template.ly")
        if outf:    
            outf.write(mm.template())
            outf.flush()
            outf.close

    if show:
        print mm.showChords(key)
    if progressions:
        print mm.printProgressions(key)
        
    sys.exit()

if __name__ == '__main__':
    main()

