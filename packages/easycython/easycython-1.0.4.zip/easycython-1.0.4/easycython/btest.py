import begin
import glob

@begin.start
def main(*filename):
    print type(filename)
    print filename
    for f in filename:
        for x in glob.glob(f):
            print x
