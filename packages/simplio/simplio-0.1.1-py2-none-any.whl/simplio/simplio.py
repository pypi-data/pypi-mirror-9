import sys


def simplio(func):
    """
    Simple command-line IO.
    Function decorator that passes input, output file objects as arguments.
    Determines if input and output are command-line argument file names or
    STDIN and STDOUT, or mix of one of each.
    """
    argc = len(sys.argv)

    if argc == 3:
        infile = open(sys.argv[1], 'r')
        outfile = open(sys.argv[2], 'w')
    elif argc == 2:
        if not sys.stdin.isatty():
            infile = sys.stdin
            outfile = open(sys.argv[1], 'w')
        else:
            infile = open(sys.argv[1], 'r')
            outfile = sys.stdout
    elif argc == 1 and not sys.stdin.isatty():
        infile = sys.stdin
        outfile = sys.stdout
    else:
        # TODO: more specific error handling
        raise IOError('invalid input')

    def wrapper():
        rval = func(infile, outfile)
        if not infile.closed:
            infile.close()
        if not outfile.closed:
            outfile.close()
        return rval

    return wrapper
