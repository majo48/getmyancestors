#!/usr/bin/env python3
# coding: utf-8

"""
   app.py - check for changes in data in FamilySearch Tree

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
import json
import sys
import time
from datetime import datetime
from checkmyancestors import databasemodule as dbm
from checkmyancestors import sessionmodule as sem

#global variables
global_timestamp = None


class PersonObj:
    """ person object in this application
        Args:
            personid (str):  person id
            generation (int):  generation relative to reference person
            referenceid (str): the person id of the person with generation = 0
            status (list): HTTP status codes from FamilySearch person and history downloads
            fsperson (dict): family search dictionary downloaded for the person id
            fsperson_changes (dict): change history for person id
    """

    def __init__(self, personid, generation, referenceid, status, fsperson, fsperson_changes):
        #
        # parameters
        self.personid = personid
        self.generation = generation
        self.referenceid = referenceid
        self.status_list = json.dumps(status)
        self.fsperson = json.dumps(fsperson)
        self.timestamp = global_timestamp
        if fsperson is not None:
            # FamilySearch.person.display
            disp = read_nested_dict(fsperson, "persons", 0, "display")
            self.name = read_nested_dict(disp, "name")
            self.gender = read_nested_dict(disp, "gender")
            self.born = read_nested_dict(disp, "birthDate")
            self.lifespan = read_nested_dict(disp, "lifespan")
            # FamilySearch.childAndParentsRelationships.person1(person2)
            parents = self.get_parents(fsperson)
            self.fatherid = parents["father"]
            self.motherid = parents["mother"]
            # FamilySearch.person.relationships(list) for person
            relationships = read_nested_dict(fsperson, "relationships")
            relationships_asc = sorted( relationships, key=lambda k: k['id'])
            self.relationships = json.dumps(relationships_asc)
        else:
            self.name = None
            self.gender = None
            self.born = None
            self.lifespan = None
            self.fatherid = None
            self.motherid = None
            self.relationships = None
        if fsperson_changes is not None:
            # FamilySearch change history(dict) for person
            self.last_modified = read_nested_dict(fsperson_changes, "updated")
        else:
            self.last_modified = None

    def get_parents(self, fsperson):
        """ read father and mother from family search person dictionary
            Args:
                fsperson (dict): family search dictionary downloaded for the person id
            Return:
                (dict):          {"father": "abc", "mother": "def"}
        """
        try:
            if "childAndParentsRelationships" in fsperson:
                for rel in fsperson["childAndParentsRelationships"]:
                    father = rel["parent1"]["resourceId"] if "parent1" in rel else None
                    mother = rel["parent2"]["resourceId"] if "parent2" in rel else None
                    child = rel["child"]["resourceId"] if "child" in rel else None
                    if child == self.personid:
                        return {"father": father, "mother": mother}
            return {"father": None, "mother": None}
        except Exception as err:
            write_log("Exception(1): key '"+err.args[0]+"' not found in FS.childAndParentsRelationships.")
            return {"father": None, "mother": None}

    def too_many_requests(self):
        """ check for HTTP error code 429: too many requests """
        if 429 in json.loads(self.status_list):
            write_log('HTTP error 429: too many requests')
            return True
        else:
            return False

# ----------


def read_nested_dict(fsdict: dict, *args):
    """
        Extract the arguments part from the dictionary data from FamilySearch.
        If missing or changed indexes to the data, the value persisted is None.
        Args:
            fsdict (dict): dictionary, complex, nested
            *args (tuple): sequence of indexes in above dictionary
        Returns:
            value (str, int, list, or dict)
    """
    try:
        x = fsdict.copy()
        for y in args:
            if isinstance(x, dict):
                x = x.get(y)
            elif isinstance(x, list):
                x = x.pop(y)
            else:
                return None
        return x
    except Exception as err:
        write_log("Exception(2): index '"+err.args[0]+"' not found in FS.parents.")
        return None

# ----------


def write_log(text):
    """ write text in the log file """
    log = "[%s]: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text)
    sys.stderr.write(log)

# ----------


def get_person_object(person_id: str, generation: int, reference_id: str, fs: sem.Session):
    """ download person data from the FamilySearch site """
    fs_person = fs.get_person(person_id)
    fs_status = [ fs.status_code ]
    fs_change = fs.get_change_history_person(person_id)
    fs_status.append(fs.status_code)
    return PersonObj(person_id, generation, reference_id, fs_status, fs_person, fs_change)

# ----------


def checkmyancestors(args):
    """
    This is the heavy lifting part of the application, persisting FamilySearch data in a database.
    The database also contains created, updated, deleted metadata for all ancestors
    """
    global global_timestamp
    now = datetime.now()
    global_timestamp = int(datetime.timestamp(now))
    # objects
    db = dbm.Database() # SQLlite database
    fs = sem.Session(args.username, args.password, timeout=10) # FamilySearch
    # reference_id
    reference_id = fs.fid
    if args.individual is not None:
        reference_id = args.individual
    # initialize loop
    changes = []
    person_count = 0
    todolist = []
    todolist.append(
        {'personid': reference_id, 'generation': 0, 'referenceid': reference_id}
    )
    while todolist:
        # loop thru all ancestors in the list
        todo = todolist.pop(0)
        person: PersonObj = get_person_object( todo['personid'], todo['generation'], todo['referenceid'], fs )
        changes = changes + db.persist_person(person)
        write_log('Person: ID='+person.personid+', Name='+person.name+' ('+person.lifespan+')')
        person_count += 1
        # check HTTP status code
        if person.too_many_requests():
            break
        # check person's father
        if ((person.fatherid is not None) and
            ((args.type == 'bioline') or (args.type == 'patriline'))):
            todolist.append(
                {'personid': person.fatherid, 'generation': person.generation+1, 'referenceid': reference_id}
            )
        # check person's mother
        if ((person.motherid is not None) and
            ((args.type == 'bioline') or (args.type == 'matriline'))):
            todolist.append(
                {'personid': person.motherid, 'generation': person.generation+1, 'referenceid': reference_id}
            )
    db.persist_session(global_timestamp, reference_id, person_count, changes)

# ----------


def main():
    """
        main: checkmyancestors/app.py
    """
    print('This module is not a script, but part of the checkmyancestors application.')


if __name__ == "__main__":
    main()
