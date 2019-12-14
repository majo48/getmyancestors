#!/usr/bin/env python3
# coding: utf-8
"""
   sessionmodule.py - login to FamilySearch and check current ancestors

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


class Session:
    """
        HTML session for accessing FamilySearch ancestors.
    """

    def __init__(self):
        print('initialized html session')
        dummy='stop'  #todo continue here


def checker(args, database):
    """
    Check for changes in the FamilySearch database for the ancestors of a reference person.

    Args:
        args ():        arguments passed to the script
        database ():    persisted ancestor data (SQLite)

    Returns:

    """
    print('SQLite version: '+database.version())
    dummy = 'stop'


def main():
    """
        main: databasemodule.py
    """
    dummy = 'stop'  #todo continue here

if __name__ == "__main__":
            main()