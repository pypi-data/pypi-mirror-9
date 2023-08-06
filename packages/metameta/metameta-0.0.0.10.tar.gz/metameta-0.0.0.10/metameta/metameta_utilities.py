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
entry_generator
output
verify_fasta_fastq_sam
'''

__version__ = '0.0.0.5'

import argparse
import re
import sys

def entry_generator(in_file, file_type):
    '''Generates and returns entries for FASTA, FASTQ, and SAM files

    Input:

        in_file:
                The FASTA, FASTQ, or SAM file to generate entries from

        file_type:
                ['fasta', 'fastq', 'sam']

    Output:
            This function is a generator so it can repeatedly yield
            entries. Each yielded entry is a list where each item
            is a different line of the entry. As such, SAM files
            have a single item, FASTA files have two, and FASTQ files
            have four.
    '''
    
    entryParts = []
    with open(in_file, 'rU') as in_handle:
        for line in in_handle:
            if line == '\n':
                    print('There is an empy line in: ' + in_file)
                    sys.exit(1)
            entryPartsLength = len(entryParts)
            if file_type == 'fasta':
                if line.startswith('@'):
                    print(in_file + ' may be a mixture of FASTA and FASTQ'\
                          + ' files.')
                    print('Suspect line follows: ')
                    print(line)
                    sys.exit(1)
                elif entryPartsLength == 0:
                    entryParts.append(line)
                elif line.startswith('>') and entryPartsLength == 2:
                    yield entryParts
                    entryParts = []
                    entryParts.append(line)
                elif not line.startswith('>'):
                    try:
                        entryParts[1] = entryParts[1].replace('\n', line)
                    except IndexError:
                        entryParts.append(line)
                else:
                    print('Unknown error with file.')
                    sys.exit(1)
            elif file_type == 'fastq':
                if line.startswith('>') and entryPartsLength < 3:
                    print(in_file + ' may be a mixture of FASTA and FASTQ'\
                          + ' files.')
                    print('Suspect line follows: ')
                    print(line)
                    sys.exit(1)
                elif entryPartsLength == 0:
                    entryParts.append(line)
                elif entryPartsLength == 1:
                    entryParts.append(line)
                elif not line.startswith('+') and entryPartsLength == 2:
                    entryParts[1] = entryParts[1].replace('\n', line)
                elif line.startswith('+') and entryPartsLength == 2:
                    entryParts.append(line)
                elif entryPartsLength == 3:
                    entryParts.append(line)
                elif len(entryParts[3]) > len(entryParts[1]):
                    print('Number of bases and quality scores do no match.')
                    print('The entry containing the error follows:\n')
                    for part in entryParts:
                        wholeEntry += part
                    print(wholeEntry)
                    sys.exit(1)
                elif entryPartsLength == 4 and len(entryParts[1]) !=\
                        len(entryParts[3]):
                    entryParts[3] = entryParts[3].replace('\n', line)
                elif entryPartsLength == 4 and len(entryParts[1]) ==\
                        len(entryParts[3]):
                    yield entryParts
                    entryParts = []
                    entryParts.append(line)
                else:
                    print('Unknown error with file.')
                    sys.exit(1)
            elif file_type == 'sam':
                if not line.startswith('@'):
                    parts = line.split('\t')
                    for part in parts:
                        entryParts.append(part)
                    yield entryParts
                    entryParts = []
            else:
                print(file_type + ' is not an acceptable file type.')
                print('File type must be "fasta", "fastq", or "sam".')
                sys.exit(1)
        else: #yield entryParts at EOF so that last entry is not lost
            if entryParts != []:
                yield entryParts

def output(message, program_verbosity, message_verbosity, log_file = None,\
           fatal = False):
    '''Writes a verbosity dependant message to log file or STDOUT

    Input:

        message:
                A message to be output to a log file
                or STDOUT.

        program_verbosity:
                The verbosity setting of the program
                calling this function. This variable
                is an integer.

        message_verbosity:
                The verbosity setting of the message
                to be written. This variable
                is an integer.

        log_file:
                An optional log file to write the
                message to in place of STDOUT.

        fatal:
                Defaults to False, if True the
                program is terminated after the
                message is written.
        
    Output:
            The message from input, only output
            if message_verbosity is equal to or
            greather than program_verbosity.

        The message is written to STDOUT unless a log file is specified,
    then it writes to the log file. The message is only written if the
    message verbosity setting exceeds the verbosity setting of the
    progam. This offers a way to control the level of output such that
    a higher program verbosity results in more output. The fatality setting
    indicates whether or not to exit the program after the message is
    written. The log file and fatality settings default to None.
    '''
    
    if int(program_verbosity) >= int(message_verbosity):
        if log_file == None:
            print(message)
        else:
            with open(log_file, 'aU') as out_handle:
                out_handle.write(message)
    if fatal == True:
        sys.exit(1)

def verify_fasta_fastq_sam(in_file):
    '''Checks a given file to see if it is a valid FASTA or FASTQ file

    Input:

        in_file:
                The file to verify
    
    Output:
            A tuple with input file and file type
            (input file, ['fasta', 'fastq', 'sam'])

        This function determines whether a file is a FASTA, FASTQ, or
    SAM file by the file's first few characters. It then uses a file
    type dependant regular expression to analyze each entry in the file.
    If a file entry does not match the regular expression then the regular
    expression and entry are broken into parts so that the user is given
    a more precise error message.
        This function is fairly quick but may take some time on large
    files since it is iterating over every line of the file. Regular
    expressions do help to speed this process up. The tradeoff in speed
    is made up by a very picky verification that nearly garuntees that
    no file-related error will occur in the script using the file.
    '''

    with open(in_file, 'rU') as in_handle:
        wholeEntry = ''
        fileType = ''
        regexString = ''
        for line in in_handle:
            if line.startswith(('@HD', '@RG', '@SQ', '@PG', '@CO', '@SN')):
                fileType = 'sam'
                regexString = r'^[!-?A-~]{1,255}\t'\
                              + r'([0-9]{1,4}|[0-5][0-9]{4}|'\
                              + r'[0-9]{1,4}|[1-5][0-9]{4}|'\
                              + r'6[0-4][0-9]{3}|65[0-4][0-9]{2}|'\
                              + r'655[0-2][0-9]|6553[0-7])\t'\
                              + r'\*|[!-()+-<>-~][!-~]*\t'\
                              + r'([0-9]{1,9}|1[0-9]{9}|2(0[0-9]{8}|'\
                              + r'1([0-3][0-9]{7}|4([0-6][0-9]{6}|'\
                              + r'7([0-3][0-9]{5}|4([0-7][0-9]{4}|'\
                              + r'8([0-2][0-9]{3}|3([0-5][0-9]{2}|'\
                              + r'6([0-3][0-9]|4[0-7])))))))))\t'\
                              + r'([0-9]{1,2}|1[0-9]{2}|'\
                              + r'2[0-4][0-9]|25[0-5])\t'\
                              + r'\*|([0-9]+[MIDNSHPX=])+\t'\
                              + r'\*|=|[!-()+-<>-~][!-~]*\t'\
                              + r'([0-9]{1,9}|1[0-9]{9}|2(0[0-9]{8}|'\
                              + r'1([0-3][0-9]{7}|4([0-6][0-9]{6}|'\
                              + r'7([0-3][0-9]{5}|4([0-7][0-9]{4}|'\
                              + r'8([0-2][0-9]{3}|3([0-5][0-9]{2}|'\
                              + r'6([0-3][0-9]|4[0-7])))))))))\t'\
                              + r'-?([0-9]{1,9}|1[0-9]{9}|2(0[0-9]{8}|'\
                              + r'1([0-3][0-9]{7}|4([0-6][0-9]{6}|'\
                              + r'7([0-3][0-9]{5}|4([0-7][0-9]{4}|'\
                              + r'8([0-2][0-9]{3}|3([0-5][0-9]{2}|'\
                              + r'6([0-3][0-9]|4[0-7])))))))))\t'\
                              + r'\*|[A-Za-z=.]+\t'\
                              + r'[!-~]+\n&'
            elif line.startswith('>'):
                fileType = 'fasta'
                regexString = r'^>.+\n[ACGTURYKMSWBDHVNX]+\n$'
            elif line.startswith('@'):
                fileType = 'fastq'
                regexString = r'^@.+\n[ACGTURYKMSWBDHVNX]+\n\+.*\n.+\n$'
            else:
                print(in_file + ' is not a properly formatted FASTA, '\
                    + 'FASTQ, or SAM file.')
                sys.exit(1)
            break #Only read first line of file
        for entry in entry_generator(in_file, fileType):
            for part in entry:
                wholeEntry += part
            matches = re.findall(regexString, wholeEntry)
            if len(matches) != 1:
                if fileType == 'sam':
                    splitRegex = regexString[1:-1].split(r'\t')
                    splitEntry = wholeEntry.split('\t')
                else:
                    splitRegex = regexString[1:-1].split(r'\n')
                    splitEntry = wholeEntry.split('\n')
                for regex, entry in zip(splitRegex[:-1], splitEntry[:-1]):
                    if not regex.startswith('^'):
                        regex = '^' + regex
                    if not regex.endswith('$'):
                        regex += '$'
                    splitMatches = re.findall(regex, entry)
                    if len(splitMatches) != 1:
                        print('The following line:\n')
                        print(entry)
                        print('\nDoes not match the regular expression:\n')
                        print(regex)
                        print('\nSee https://docs.python.org/3.4/'\
                              + 'library/re.html for information '\
                              + 'on how to interpret regular expressions.')
                        print('\nThe entire entry containing the error'\
                              + ' follows:\n')
                        print(wholeEntry)
            wholeEntry = ''
    return (in_file, fileType)
    
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
        'entry_generator': entry_generator,
        'output': output,
        'verify_fasta_fastq_sam': verify_fasta_fastq_sam,
        }
    
    if args.version:
        print(__version__)
        sys.exit(0)
    elif args.functions == None:
        print(__doc__)
        sys.exit(0)
    else:
        for function in args.functions:
            try:
                print(dict_functions[function].__doc__)
                print()
            except KeyError:
                print('\nThere is no such function: ' + function + '\n')
                sys.exit(1)
    sys.exit(0)
