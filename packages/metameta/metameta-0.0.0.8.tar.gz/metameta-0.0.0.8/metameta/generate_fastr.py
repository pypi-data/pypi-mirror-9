#!/usr/bin/env python

'''obtains read depth data for a FASTA/Q file from a SAM file

Usage:

    generate_fastr.py [--version] <FASTA_Q_file> <SAM_file>

    generate_fastr produce a FASTR file containing per base per entry
    read depth data given a FASTA or FASTQ file and a SAM file.

FASTR Format:
    The FASTR Format is identical to the FASTA Format except the
bases are replaced by numbers representing the read depth of the
corresponding bases in the given FASTA file. Since read depth
numbers may contain more than one digit (e.g. a read depth of
10) so each number is seperated by a hyphen.
'''

__version__ = '0.0.0.3'

import argparse
from metameta_utilities import output, verify_fasta_fastq_sam

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = __doc__,
                                        formatter_class = argparse.\
                                        RawDescriptionHelpFormatter)
    parser.add_argument('fasta_q_file',
                        type = verify_fasta_fastq_sam,
                        default = None,
                        nargs = '?',
                        help = 'FASTA or FASTQ file to analyze the read' +\
                        ' depth of using the given SAM file')
    parser.add_argument('sam_file',
                        type = verify_fasta_fastq_sam,
                        default = None,
                        nargs = '?',
                        help = 'SAM file containing mapping data for' + \
                        'given FASTA/Q file')
    parser.add_argument('-v', '--version',
                        action = 'store_true',
                        help = 'prints tool version and exits')
    args = parser.parse_args()

    if args.version:
        print(__version__)
    elif args.fasta_q_file == None and args.sam_file == None:
        print(__doc__)
    elif args.fasta_q_file != None and args.sam_file == None:
        output('No SAM file specified.', 1, 1, fatal = True)
    elif args.fasta_q_file == None and args.sam_file != None: 
        output('No FASTA/Q file specified.', 1, 1, fatal = True)
    else:
        #TODO: call main function
        pass
