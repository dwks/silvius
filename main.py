# Main

from scan import scan
from parse import parse

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    f = open(filename)
    while True:
        line = f.readline()
        if line == '': break
        parse(scan(line))
    f.close()

    print 'ok'
