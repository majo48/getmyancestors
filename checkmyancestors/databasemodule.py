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

    def _get_person(self, personid, referenceid):
        """
        Get the most recent persisted person with personid and referenceid from the SQLite database
        Args:
            personid (str):
            referenceid (str):
        Returns:
            (list) with the most recent matching record (dict) in [0] or None
        """
        conn: Connection = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor: Cursor = conn.cursor()
        sql = 'SELECT * FROM persons WHERE personid = ? AND referenceid = ? ORDER BY timestamp DESC'
        try:
            cursor.execute( sql, (personid, referenceid))
            rows = [dict(row) for row in cursor.fetchall()] # convert sqlite3.Row
            return rows
        #
        except sqlite3.Error as e:
            app.write_log("SQLite INSERT person error occurred:", e.args[0])
            return None

    def persist_person(self, person):
        """ persist person to database conditionally
            Args:
                 person (app.PersonObj): object data downloaded from FamilySearch
            Result:
                (list): list with changes in person object
        """
        chgs = []
        rows = self._get_person(person.personid, person.referenceid)
        if rows:
            # compare downloaded person data to the persisted person data
            row = rows[0]
            if person.status_list != row['status_list']:
                chgs.append('Status of HTTP codes has changed to '+person.status_list+'.')
            if person.generation != row['generation']:
                chgs.append('The generation number has changed to '+str(person.generation)+'.')
            if person.name != row['name']:
                chgs.append('The name has changed from '+row['name']+' to '+person.name+'.')
            if person.gender != row['gender']:
                chgs.append('The gender has changed to '+person.gender+'.')
            if person.born != row['born']:
                chgs.append('The birth date has changed from '+row['born']+' to '+person.born+'.')
            if person.lifespan != row['lifespan']:
                chgs.append('The lifespan has changed from '+row['lifespan']+' to '+person.lifespan+'.')
            if person.fatherid != row['fatherid']:
                chgs.append('The fatherid has changed from ' + row['fatherid'] + ' to ' + person.fatherid + '.')
            if person.motherid != row['motherid']:
                chgs.append('The motherid has changed from ' + row['motherid'] + ' to ' + person.motherid + '.')
            if person.relationships != row['relationships']:
                chgs.append('Change in relationships: father, mother, spouse, or children.')
            if person.last_modified != row['last_modified']:
                chgs.append('Change(s) in the persons change history.')
            if chgs:
                chgs.insert(0, 'Changes detected in object: '+person.personid)
                lines = ''
                for line in chgs:
                    lines +=  line + '\n'
                app.write_log(lines[:-2])
                # add object to the SQLite database
                self._insert_person(person)
        else:
            # new object in the SQLite database
            self._insert_person(person)
        return chgs


def main():
    """
        main@databasemodule.py
    """
    dummy = 'stop'  #todo continue here...


if __name__ == "__main__":
            main()