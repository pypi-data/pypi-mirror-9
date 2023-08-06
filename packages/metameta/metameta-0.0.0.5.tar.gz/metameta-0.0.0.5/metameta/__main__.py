#!/usr/bin/env python

'''metameta - metatranscriptome to metagenome mapping analysis toolset

Usage:

    metameta <tool> [arguments for tool]

    metameta with no <tool> or arguments will give help on the package
    <tool> without any arguments will give the help for that tool

Tools:
'''

import sys
import subprocess
import argparse

def tool_check(desired_tool):
    tools = ['test']
    for tool in tools:
        if desired_tool == tool:
            return desired_tool
    print('No such tool: ' + desired_tool)
    print('Available tools:')
    for tool in tools:
        print(tool)
    sys.exit(1)

def main()
    parser = argparse.ArgumentParser(description = __doc__,
                                     formatter_class=argparse.\
                                     RawDescriptionHelpFormatter)
    parser.add_argument('tool',
                        type = tool_check,
                        default = None,
                        nargs = '?',
                        help = 'tool to run')
    parser.add_argument('arguments',
                        nargs = argparse.REMAINDER,
                        help = 'arguments to pass to tool')
    args = parser.parse_args()
    
    if args.tool == None:
        print(__doc__)
    elif args.arguments == [] and args.tool != None:
        script = 'metameta/' + args.tool + '.py'
        subprocess.call(['python', script])
    else:
        pass
        #TODO: call other program with subprocess
