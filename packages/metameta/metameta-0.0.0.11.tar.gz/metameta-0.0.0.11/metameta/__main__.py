#!/usr/bin/env python

'''metameta - metatranscriptome to metagenome mapping analysis toolset

Usage:

    metameta [--version] <tool> [arguments for tool]

"metameta" without arguments will give help on the metameta package.
"metameta <tool>" without any arguments will give the help for that tool.
"--verify" in any tool verifies input files before use.

Verbosity Settings (after <tool>):

    -v: Fatal errors and important information printed
    -vv: Detailed information on everything the program is doing,
           best reserved for debugging purposes
    Note: any numbers of "v"s may be specified but anything greater than
          -vv will be identical to -vv. Fatal errors are printed be default.   

Tools:

    generate_fastr

            Generates a FASTR file containing per base read depth data
            of a given FASTA or FASTQ file.

    metameta_utilities:

            A file containing a variety of modules useful to many scripts in
            metameta.
'''

__version__ = '0.0.0.11'

import argparse
import subprocess
import sys

def tool_check(desired_tool):
    '''Checks if given tool is valid and prints a list of toosl if not'''
    
    tools = [
        'metameta_utilities',
        'generate_fastr'
        ]
    for tool in tools:
        if desired_tool == tool:
            return desired_tool
    print('No such tool: ' + desired_tool)
    print('Available tools:')
    for tool in tools:
        print(tool)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description = __doc__,
                                        formatter_class = argparse.\
                                        RawDescriptionHelpFormatter)
    parser.add_argument('tool',
                        type = tool_check,
                        default = None,
                        nargs = '?',
                        help = 'tool to run')
    parser.add_argument('arguments',
                        nargs = argparse.REMAINDER,
                        help = 'arguments to pass to tool')
    parser.add_argument('-v',' --version',
                        help = 'prints package version and exits',
                        action = 'store_true')
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)
    elif args.tool == None:
        print(__doc__)
        sys.exit(0)
    elif args.arguments == [] and args.tool != None:
        script = 'metameta/' + args.tool + '.py'
        subprocess.call(['python', script])
    
if __name__ == '__main__':
    main()
    sys.exit(0)
