#!/usr/bin/env python3
# coding: utf-8
"""
   databasemodule.py - FamilySearch change history

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
import os
import sqlite3


class Database:
    """
        SQLite database for persisting FamilySearch ancestors.
    """

    def __init__(self):
        """ initialize the SQLite database"""
        path = os.path.dirname(os.path.realpath(__file__))
        conn = sqlite3.connect(path + '/' + 'database.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "persons" (
        	    "personid"      TEXT NOT NULL,
	            "timestamp"	    INTEGER NOT NULL,
	            "referenceid"   TEXT NOT NULL,
	            "status_list"   TEXT NOT NULL,
	            "generation"    INTEGER NOT NULL,
	            "fsperson"      TEXT,
	            "name"          TEXT,
	            "gender"        TEXT,
	            "born"          TEXT,
	            "lifespan"      TEXT,
	            "fatherid"      TEXT,
	            "motherid"      TEXT,
	            "relationships" TEXT,
	            "last_modified" INTEGER,
	            PRIMARY KEY("personid","timestamp","referenceid")
                );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "sessions" (
	            "timestamp"    INTEGER NOT NULL,
	            "person_count"  INTEGER NOT NULL,
	            "status"       TEXT,
	            "change_log"    TEXT,
	            PRIMARY KEY("timestamp")
                );
        """)

    def persist_person(self, person):
        """ persist person to database
            Args:
                 person (PersonObj): object data downloaded from FamilySearch
        """
        print("persisted " + person.name + ', ' + person.lifespan + "[" + str(person.generation) + "]")
        #todo continue here...


def main():
    """
        main@databasemodule.py
    """
    dummy = 'stop'  #todo continue here...


if __name__ == "__main__":
            main()