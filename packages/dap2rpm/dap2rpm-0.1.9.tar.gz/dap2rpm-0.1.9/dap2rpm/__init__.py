# -*- coding: utf-8 -*-

import argparse
import sys

from dap2rpm import dap
from dap2rpm import setup

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dap', help='Name of DAP on DAPI or path to local DAP')
    parser.add_argument('-v', '--version', default=None,
                        help='Name of DAP version to generate spec for; ignored with local DAP')
    parser.add_argument('-f', '--files', action='store_true',
                        help='Include all files in the %%files section in SPEC (not recommended)')
    parser.add_argument('-l', '--filelist', action='store_true',
                        help='Output only the list of %%files (used during %%assistant_install)')
    parser.add_argument('-L', '--license', default=None, nargs='+',
                        help='List these filenames (stored under \'doc\') under the %%license tag.')
    parser.add_argument('-s', '--save-dap', default=None, metavar='LOCATION',
                        help='Save the DAP to a given directory (useful especially ' +
                             'when downloading from DAPI)')
    args = vars(parser.parse_args())

    try:
        setup.setup()
    except:
        # TODO: log error
        sys.exit(1)

    d = dap.DAP.get_dap(args['dap'], args['version'], args['save_dap'], args['license'])

    if args['filelist']:
        print(d.render_files())
    elif args['files']:
        print(d.render_spec(include_files=True))
    else:
        print(d.render_spec())
