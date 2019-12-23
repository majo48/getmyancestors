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
from sqlite3.dbapi2 import Connection, Cursor
from checkmyancestors import app

class Database:
    """
        SQLite database for persisting FamilySearch ancestors.
    """

    def __init__(self):
        """ initialize the SQLite database"""
        conn: Connection = self._get_connection()
        cursor: Cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
        	        personid      TEXT NOT NULL,
	                timestamp	  INTEGER NOT NULL,
	                referenceid   TEXT NOT NULL,
	                status_list   TEXT NOT NULL,
	                generation    INTEGER NOT NULL,
	                fsperson      TEXT,
	                name          TEXT,
	                gender        TEXT,
	                born          TEXT,
	                lifespan      TEXT,
	                fatherid      TEXT,
	                motherid      TEXT,
	                relationships TEXT,
	                last_modified INTEGER,
	                PRIMARY KEY(personid,timestamp,referenceid)); """)
            conn.commit()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
	                timestamp     INTEGER NOT NULL,
	                person_count  INTEGER NOT NULL,
	                status        TEXT,
	                change_log    TEXT,
	                PRIMARY KEY(timestamp)); """)
            conn.commit()
            conn.close()
        #
        except sqlite3.Error as e:
            app.write_log("SQLite CREATE TABLE error occurred:", e.args[0])

    def _get_connection(self):
        """ get SQLite connection object """
        path = os.path.dirname(os.path.realpath(__file__))
        return sqlite3.connect(path + '/' + 'database.db')

    def _insert_person(self, person):
        """ insert the person object in the SQLite database
            Args:
                 person (app.PersonObj): object data downloaded from FamilySearch
        """
        conn: Connection = self._get_connection()
        cursor: Cursor = conn.cursor()
        sql = """
            INSERT INTO persons 
                (personid, timestamp, referenceid, status_list, generation, 
                 fsperson, name, gender, born, lifespan, 
                 fatherid, motherid, relationships, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute( sql,
                (person.personid, person.timestamp, person.referenceid, person.status_list, person.generation,
                 person.fsperson, person.name, person.gender, person.born, person.lifespan,
                 person.fatherid, person.motherid, person.relationships, person.last_modified))
            conn.commit()
            conn.close()
        #
        except sqlite3.Error as e:
            app.write_log("SQLite INSERT person error occurred:", e.args[0])

    def persist_person(self, person):
        """ persist person to database conditionally
            Args:
                 person (app.PersonObj): object data downloaded from FamilySearch
        """
        self._insert_person(person)


def main():
    """
        main@databasemodule.py
    """
    dummy = 'stop'  #todo continue here...


if __name__ == "__main__":
            main()