#!/usr/bin/python

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


'''
Save columns from SPEC data file scan(s) to TSV files

.. note:: TSV: tab-separated values

**Usage**::

  extractSpecScan.py /tmp/CeCoIn5 -s 5 -c HerixE Ana5 ICO-C
  extractSpecScan.py ./testdata/11_03_Vinod.dat   -s 2 12   -c USAXS.m2rp Monitor  I0

**General usage**::

    usage: extractSpecScan [-h] [--nolabels] [-s SCAN [SCAN ...]] [-c COLUMN [COLUMN ...]] spec_file

Save columns from SPEC data file scan(s) to TSV files


positional arguments:

========================  ==========================================================================
argument                  description
========================  ==========================================================================
spec_file                 SPEC data file name (path is optional, can use relative or absolute)
========================  ==========================================================================


optional arguments:

=============================  ==========================================================================
argument                       description
=============================  ==========================================================================
-h, --help                     show this help message and exit
-v, --version                  show the version and exit
--nolabels                     do not write column labels to output file (default: write labels)
-s SCAN [SCAN ...]             scan number(s) to be extracted, must be integers
--scan SCAN [SCAN ...]         same as *-s* option
-c COLUMN [COLUMN ...]         column label(s) to be extracted
--column COLUMN [COLUMN ...]   same as *-c* option
=============================  ==========================================================================

.. note:: column names MUST appear in all chosen scans

Compatible with Python 2.7+
'''

__url__ = 'http://spec2nexus.readthedocs.org/en/latest/extractSpecScan.html'

import os
import sys
import spec
import spec2nexus


#-------------------------------------------------------------------------------------------


REPORTING_QUIET    = 'quiet'
REPORTING_STANDARD = 'standard'
REPORTING_VERBOSE  = 'verbose'


#-------------------------------------------------------------------------------------------


def makeOutputFileName(specFile, scanNum):
    '''
    return an output file name based on specFile and scanNum
    
    :param str specFile: name of existing SPEC data file to be read
    :param int scanNum: number of chosen SPEC scan

    append scanNum to specFile to get output file name 
    (before file extension if present)
    
    Always add a file extension to the output file.
    If none is present, use ".dat".
    
    Examples:
    
    ===========  =======   ==============
    specFile     scanNum   outFile
    ===========  =======   ==============
    CeCoIn5      scan 5    CeCoIn5_5.dat
    CeCoIn5.dat  scan 77   CeCoIn5_77.dat
    ===========  =======   ==============
    '''
    name_parts = os.path.splitext(specFile)
    outFile = name_parts[0] + '_' + str(scanNum) + name_parts[1]
    return outFile


def get_user_parameters():
    '''configure user's command line parameters from sys.argv'''
    import argparse
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __url__
    doc += '\n  v' + spec2nexus.__version__
    parser = argparse.ArgumentParser(prog='extractSpecScan', description=doc)

    parser.add_argument('-v',
                        '--version', 
                        action='version',
                        help='print version number and exit',
                        version=spec2nexus.__version__)
    msg = 'do not write column labels to output file (default: write labels)'
    parser.add_argument('--nolabels', 
                        action='store_true',
                        help=msg,
                        default=False)
    parser.add_argument('spec_file',
                        action='store', 
                        help="SPEC data file name(s)")
    msg = "scan number(s) to be extracted (must specify at least one)"
    parser.add_argument('-s',
                        '--scan', 
                        action='store', 
                        nargs='+', 
                        type=int,
                        required=True,
                        help=msg)
    msg = "column label(s) to be extracted (must specify at least one)"
    parser.add_argument('-c',
                        '--column', 
                        action='store',
                        nargs='+', 
                        required=True,
                        help=msg)

    group = parser.add_mutually_exclusive_group()
    group.set_defaults(reporting_level=REPORTING_STANDARD)
    msg =  'suppress all program output (except errors)'
    msg += ', do not use with --verbose option'
    group.add_argument('--quiet', 
                       dest='reporting_level',
                       action='store_const',
                       const=REPORTING_QUIET,
                       help=msg)
    msg =  'print more program output'
    msg += ', do not use with --quiet option'
    group.add_argument('--verbose', 
                       dest='reporting_level',
                       action='store_const',
                       const=REPORTING_VERBOSE,
                       help=msg)

    args = parser.parse_args()
    
    args.print_labels = not args.nolabels
    del args.nolabels

    return args


def main():
    '''
    read the data file, find each scan, find the columns, save the data
    
    :param [str] cmdArgs: Namespace from argparse, returned from get_user_parameters()
    
    ..  such as:
      Namespace(column=['mr', 'I0', 'USAXS_PD'], print_labels=True, scan=[1, 6], spec_file=['data/APS_spec_data.dat'])
    
    .. note:: Each column label must match *exactly* the name of a label
       in each chosen SPEC scan number or the program will skip that particular scan
       
       If more than one column matches, the first match will be selected.
    
    example output::

        # mr    I0    USAXS_PD
        1.9475    65024    276
        1.9725    64845    352
        1.9975    65449    478
    
    '''
    cmdArgs = get_user_parameters()

    if cmdArgs.reporting_level in (REPORTING_STANDARD, REPORTING_VERBOSE):
        print "program: " + sys.argv[0]
    # now open the file and read it
    specData = spec.SpecDataFile(cmdArgs.spec_file)
    if cmdArgs.reporting_level in (REPORTING_STANDARD, REPORTING_VERBOSE):
        print "read: " + cmdArgs.spec_file
    
    for scanNum in cmdArgs.scan:
        outFile = makeOutputFileName(cmdArgs.spec_file, scanNum)
        scan = specData.getScan(scanNum)
    
        # get the column numbers corresponding to the column_labels
        column_numbers = []
        for label in cmdArgs.column:
            if label in scan.L:
                # report all columns in order specified on command-line
                column_numbers.append( scan.L.index(label) )
            else:
                if cmdArgs.reporting_level in (REPORTING_VERBOSE):
                    msg = 'column label "' + label + '" not found in scan #'
                    msg += str(scanNum) + ' ... skipping'
                    print msg       # report all mismatched column labels
    
        if len(column_numbers) == len(cmdArgs.column):   # must be perfect matches
            txt = []
            if cmdArgs.print_labels:
                txt.append( '# ' + '\t'.join(cmdArgs.column) )
            data = [scan.data[item] for item in cmdArgs.column]
            for data_row in zip(*data):
                txt.append( '\t'.join(map(str, data_row)) )
        
            fp = open(outFile, 'w')
            fp.write('\n'.join(txt))
            fp.close()
            if cmdArgs.reporting_level in (REPORTING_STANDARD, REPORTING_VERBOSE):
                print "wrote: " + outFile


if __name__ == "__main__":
    if False:
      sys.argv.append('data/APS_spec_data.dat')
      sys.argv.append('-s')
      sys.argv.append('1')
      sys.argv.append('6')
      sys.argv.append('-c')
      sys.argv.append('mr')
      sys.argv.append('USAXS_PD')
      sys.argv.append('I0')
      sys.argv.append('seconds')
    main()
