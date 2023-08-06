from distutils.core import setup
setup(name='LyMaker',
      version='0.5.1',
      description='Lilypond source file generator',
      long_description='LyMaker is a program which was designed to generate Lilypond source files. It can generate basslines, harmonies and drumlines.',	
      author='Acoustic E',
      author_email='mondlichtgestalt@gmail.com',
      packages = ['LyMaker'],
      py_modules = ['LyMaker','testLyMaker'],
    data_files=[('share/doc/packages/LyMaker', ['doc/LyMaker.pdf','changelog']),
	('share/LyMaker/examples/xml', ['examples/blues.xml','examples/rock.xml','examples/tonaljazz.xml','examples/modaljazz.xml','examples/funky.xml','examples/fusion.xml']),
	('share/LyMaker/examples/ly', ['examples/blues.ly','examples/rock.ly','examples/tonaljazz.ly','examples/modaljazz.ly','examples/funky.ly','examples/fusion.ly']),
	('share/LyMaker/examples/midi', ['examples/blues.midi','examples/rock.midi','examples/tonaljazz.midi','examples/modaljazz.midi','examples/funky.midi','examples/fusion.midi']),
	('share/LyMaker/examples/mp3', ['examples/blues.mp3','examples/rock.mp3','examples/tonaljazz.mp3','examples/modaljazz.mp3','examples/funky.mp3','examples/fusion.mp3']),
	('share/LyMaker/examples/pdf', ['examples/blues.pdf','examples/rock.pdf','examples/tonaljazz.pdf','examples/modaljazz.pdf','examples/funky.pdf','examples/fusion.pdf'])]
      )
