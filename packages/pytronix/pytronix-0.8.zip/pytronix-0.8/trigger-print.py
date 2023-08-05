import sys
from telepythic.library import TekScope

if __name__ == "__main__":
    ip = sys.argv[1]
    print 'Connecting to',ip
    dev = TekScope(sys.argv[1])
    print 'Printing to', dev.ask('HARDCopy:ACTIVe?')
    dev.write('HARDCopy')
