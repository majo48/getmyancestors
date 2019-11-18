#!/usr/bin/env python3
# coding: utf-8
# style: one module = one file
"""
   checkmyancestors.py - check for changes in data in FamilySearch Tree

   Copyright (C) 2019-2020 Martin Jonasse (mart.jonasse@gmail.com)

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
"""

# global imports
import argparse
import sys
import getpass

# getmyancestor project imports
#

def get_arguments():
    """ function: get all arguments from the command line
       :return: {Namespace}
            individual(str},
            outfile{TextIOWrapper},
            password{str},
            type{str},
            username{str}
    """
    parser = argparse.ArgumentParser(
        description="Retrieve GEDCOM data from FamilySearch Tree (4 Jul 2016)",
        add_help=False,
        usage="getmyancestors.py -u username -p password [options]",
    )
    parser.add_argument(
        "-u",
        "--username",
        metavar="<STR>",
        type=str,
        help="FamilySearch username"
    )
    parser.add_argument(
        "-p",
        "--password",
        metavar="<STR>",
        type=str,
        help="FamilySearch password"
    )
    parser.add_argument(
        "-i",
        "--individual",
        metavar="<STR>",
        type=str,
        help="FamilySearch ID for whom to retrieve ancestors",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=['patriline', 'matriline', 'bioline'],
        metavar="<STR>",
        type=str,
        default='bioline',
        help="Type of ancestors [bioline]",
    )
    # outfile argument
    try:
        parser.add_argument(
            "-o",
            "--outfile",
            metavar="<FILE>",
            type=argparse.FileType("w", encoding="UTF-8"),
            default=sys.stdout,
            help="Output file name with path [stdout]",
        )
    except TypeError:
        sys.stderr.write("Python >= 3.4 is required to run this script\n")
        sys.exit(2)
    #
    # extract arguments from the command line
    try:
        parser.error = parser.exit
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(2)
    #
    # check for missing arguments
    if args.username is None:
        args.username = input("Enter FamilySearch username: ")
    if args.password is None:
        args.password = getpass.getpass("Enter FamilySearch password: ")
    return args

def main():
    """ main: checkmyancestors.py
    """
    args = get_arguments()
    dummy = 'stop' #todo continue here

if __name__ == "__main__":
            main()