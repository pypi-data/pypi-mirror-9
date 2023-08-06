#!/usr/bin/env python

'''generic bioinformatic related functions

Usage:

    metameta_utilities.py [--version] <functions>

    <functions> will give the help for that each function
    listed (multiple functions can be specified).

This file simply contains a number of generic bioinformatic
related functions useful to many programs in metameta. It
is meant to be imported by other scripts.

Functions:
verify_fasta_fastq
'''

__version__ = '0.0.0.1'

import argparse
import re
import sys

def verify_fasta_fastq(in_file):
    '''Checks a given file to see if it is a valid FASTA or FASTQ file'''

    #TODO: Clean up this functional but messy function
    wholeEntry = []
    with open(in_file, 'rU') as in_handle:
        fileType = ''
        for line in in_handle:
            if fileType == '':
                if line.startswith('>'):
                    fileType = 'fasta'
                elif line.startswith('@'):
                    fileType = 'fastq'
                else:
                    print(in_file + ' is not a properly formatted FASTA '\
                          'or FASTQ file.')
                    sys.exit(1)
            if fileType == 'fasta':
                if line.startswith('>') and len(wholeEntry) == 2:
                    count = 0
                    for segment in wholeEntry:
                        if count == 0:
                            matches = re.findall(r'>.+\n', segment)
                            if not len(matches) == 1:
                                print('Error with FASTA heading: ' + segment)
                                sys.exit(1)
                        elif count == 1:
                            matches = re.findall(r'[^ACGTURYKMSWBDHVNX]+',\
                                                 segment)
                            if len(matches) != 1:
                                print('Error with FASTA sequence: ' +\
                                      wholeEntry[0])
                                sys.exit(1)
                        count += 1
                    wholeEntry = []
                    wholeEntry.append(line)
                elif line.startswith('>') and wholeEntry == []:
                    wholeEntry.append(line)
                elif line.startswith('@'):
                    print(in_file + ' may be a mixture of FASTA and FASTQ files.')
                    sys.exit(1)
                elif not line.startswith('>'):
                    try:
                        wholeEntry[1] = wholeEntry[1].replace('\n', line)
                    except IndexError:
                        wholeEntry.append(line)
            elif fileType == 'fastq':
                if line.startswith('>') and len(wholeEntry) == 2:
                    print(in_file + ' may be a mixture of FASTA and FASTQ files.')
                    sys.exit(1)
                elif line.startswith('@') and len(wholeEntry) == 4 and\
                        len(wholeEntry[1]) == len(wholeEntry[3]):
                    for segment in wholeEntry:
                        count = 0
                        lineLength = 0
                        if count == 0:
                            matches = re.findall(r'>.+\n', segment)
                            if not len(matches) == 1:
                                print('Error with FASTQ heading: ' + segment)
                                sys.exit(1)
                        elif count == 1:
                            lineLength = len(line)
                            matches = re.findall(r'[^ACGTURYKMSWBDHVNX]+',\
                                                 segment)
                            if len(matches) != 1:
                                print('Error with FASTQ sequence: ' + segment)
                                sys.exit(1)
                        elif count == 2:
                            matches = re.findall(r'@.*\n', line)
                            if not len(matches) == 1:
                                print('Error with FASTQ divisor: ' + segment)
                                sys.exit(1)
                        elif count == 3:
                            matches = re.findall(r'[.+]+\n', segment)
                            if not len(matches) == 1:
                                print('Error with FASTQ quality sequence: '\
                                      + segment)
                                sys.exit(1)
                            if not len(line) == lineLength:
                                print('Quality score length and sequence length '\
                                      + 'do not match.')
                                sys.exit(1)
                        count += 1
                    wholeEntry = []
                    wholeEntry.append(line)
                elif line.startswith('@') and wholeEntry == []:
                    wholeEntry.append(line)
                elif not line.startswith('@') and len(wholeEntry) == 1:
                    wholeEntry.append(line)
                elif line.startswith('+') and len(wholeEntry) == 2:
                    wholeEntry.append(line)
                elif not line.startswith('@') and len(wholeEntry) == 2:
                    wholeEntry[1] = wholeEntry[1].replace('\n', line)
                elif len(wholeEntry) == 3:
                    wholeEntry.append(line)
                elif len(wholeEntry) == 4 and len(wholeEntry[1]) !=\
                        len(wholeEntry[3]):
                    wholeEntry[3].replace('\n', line)
    return fileType
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = __doc__,
                                    formatter_class = argparse.\
                                    RawDescriptionHelpFormatter)
    parser.add_argument('functions',
                        default = None,
                        nargs = '*',
                        help = 'print function help')
    parser.add_argument('-v', '--version',
                        action = 'store_true',
                        help = 'prints tool version and exits')
    args = parser.parse_args()

    dict_functions = {
        'verify_fasta_fastq': verify_fasta_fastq
        }
    
    if args.version:
        print(__version__)
        sys.exit(0)
    elif args.functions == None:
        print(__doc__)
        sys.exit(0)
    else:
        try:
            for function in args.functions:
                print(dict_functions[function].__doc__)
        except KeyError:
            print('\nThere is no such function: ' + function + '\n')
        sys.exit(0)
