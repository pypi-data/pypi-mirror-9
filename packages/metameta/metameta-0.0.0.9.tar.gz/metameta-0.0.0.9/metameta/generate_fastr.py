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

__version__ = '0.0.0.4'

import argparse
from metameta_utilities import entry_generator, output, verify_fasta_fastq_sam
import sys

def generate_fastr(fasta_q_file, sam_file, fasta_q_file_type):
    '''Generates a FASTR file from the given FASTA/Q file and SAM file

    Input:
    
        fasta_q_file:
                A FASTA or FASTQ file containg the
                sequences that other sequences were
                mapped onto.
        
        sam_file:
                This SAM file must be generated from
                a program mapping the onto the contig
                file. I recommend using the Burrows-
                Wheeler Aligner.
                 
        fasta_q_file_type:
                ['fasta', 'fastq']

    Output:
            A FASTR file containing per base read depth data for the given
            FASTA/Q file.

        #TODO: Write overview of how function works here.
    '''

    if fasta_q_file_type != 'fasta' and fasta_q_file_type != 'fastq':
        message = fasta_q_file_type + ' is not an acceptable file type.'\
                  + ' File type must be "fasta", or "fastq".'
        output(message, 1, 1, fatal = True)
    readDepth = {}
    header = ''
    sequenceLength = 0
    sequenceDepth = []
    for entry in entry_generator(fasta_q_file, fasta_q_file_type):
        header = entry[0][1:-1]
        sequenceLength = len(entry[1][:-1])
        sequenceDepth = [0 for base in range(sequenceLength)]
        readDepth[header] = sequenceDepth
    print(readDepth)
        
    
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
        generate_fastr(args.fasta_q_file[0], args.sam_file[0],\
                       args.fasta_q_file[1])
    sys.exit(0)
