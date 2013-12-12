#!/usr/bin/env python

""" Command-line parser for an introspy generated db. """

__version__   = '0.2.0'
__author__    = "Tom Daniels & Alban Diquet"
__license__   = "See ../LICENSE"
__copyright__ = "Copyright 2013, iSEC Partners, Inc."

from sys import argv
import os
from argparse import ArgumentParser
from re import match
from DBAnalyzer import DBAnalyzer
from ScpClient import ScpClient
from DBParser import DBParser
from HTMLReportGenerator import HTMLReportGenerator
from APIGroups import APIGroups



def main(argv):

    # Parse command line
    parser = ArgumentParser(description="introspy analysis and report\
        generation tool", version=__version__)
    html_group = parser.add_argument_group('html report format options')
    html_group.add_argument("-o", "--outdir",
        help="Generate an HTML report and write it to the\
        specified directory (ignores all other command line\
        optons).")
    #cli_group = parser.add_argument_group('command-line reporting options')
    #cli_group.add_argument("-l", "--list",
    #    action="store_true",
    #    help="List traced calls (no signature analysis\
    #    performed)")
    #cli_group.add_argument("-g", "--group",
    #    choices=APIGroups.API_GROUPS_LIST,
    #    help="Filter by signature group")
    #cli_group.add_argument("-s", "--sub-group",
    #    choices=APIGroups.API_SUBGROUPS_LIST,
    #    help="Filter by signature sub-group")
    #stats_group = parser.add_argument_group('additional command-line options')
    #stats_group.add_argument("-i", "--info",
    #    choices=['urls', 'files'],#, 'keys'],
	#help="Enumerate URLs or files accessed within the traced calls")#' and keychain items, etc.")
    #stats_group.add_argument("-d", "--delete",
    #    action="store_true",
    #    help="Remove all introspy databases on a given remote device")
    parser.add_argument("db",
        help="The introspy-generated database to analyze.")#\
        #specifying an IP address causes the analyzer to fetch a\
        #remote database.")
    args = parser.parse_args()


    # Get the introspy DB
    if match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", args.db):
        # The DB is on device so we need to grab a local copy
        # TODO: Add an explicit option to specify a remote db instead of inferring this using a regexp
        scp = ScpClient(ip=args.db)
        if args.delete: # Just delete DBs on the device and quit
            scp.delete_remote_dbs()
            return
        else:
            db_path = scp.select_and_fetch_db()
    else:
        db_path = args.db


    # Process the DB
    # Make sure it's there
    if not os.path.exists(db_path): # Nice race condition
        print 'Error: Could not find the DB file.'
        return
    analyzedDB = DBAnalyzer(db_path)


    # Generate output
    if args.outdir: # Generate an HTML report
        reportGen = HTMLReportGenerator(analyzedDB)
        reportGen.write_report_to_directory(args.outdir)

    else: # Print DB info to the console

        if args.info: # Enumerate URLs/files
            if args.info == "urls":
                for url in analyzedDB.get_all_URLs():
                    print url
            elif args.info == "files":
                for path in analyzedDB.get_all_files():
                    print path
            #elif args.info == "keys":
            # TODO

        elif args.list: # Print all traced calls
            # TODO: Call print() here instead of inside the method
            analyzedDB.get_traced_calls_as_text(args.group, args.sub_group)

        else: # Print all findings
            analyzedDB.get_findings_as_text(args.group, args.sub_group)


if __name__ == "__main__":
    main(argv[1:])
