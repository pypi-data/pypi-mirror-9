#!/usr/bin/env python

import sys
import re
import argparse

import marlowe_ui.postprocess.dumper

argparser = argparse.ArgumentParser()
argparser.add_argument('input', type=argparse.FileType('rt'), help="Input file. '-' for stdin")
argparser.add_argument(
    'output', type=str, default=None, nargs='?',
    help='output data directory to output parsed data. '
    'If ommitted, INPUT.post is set INPUT.lst data file. '
    'If input is stdin, this option should be given.')
argparser.add_argument(
    '--cascade-directory-format', type=str,
    default='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}',
    help='directory form to store data for each cascade, which is created under '
    'OUTPUT directory (default: %(default)s)')

args = argparser.parse_args()

# test output directory
if args.output is None:
    if args.input.name == '<stdin>':
        print('Error: input is stdin, but no output name is provided.')
        sys.exit(1)
    else:
        # generate output name
        args.output = re.sub('\.lst$', '.post', args.input.name)
if args.output == args.input.name:
    print('Error: same input ({}) and output ({}) name'.format(args.input.name,
                                                               args.output))
    sys.exit(2)

try:
    p = marlowe_ui.postprocess.dumper.Parser(
        outputdir=args.output, cascade_dir_form=args.cascade_directory_format)
    p.parse(args.input)
except Exception as e:
    print('Error in dumper: {}'.format(e.args))
