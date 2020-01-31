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

# module variable
debug_app = False  # used in write_log


class PersonObj:
    """ person object in this application
        Args:
            personid (str):  person id
            generation (int):  generation relative to reference person
            referenceid (str): the person id of the person with generation = 0
            status_list (list): HTTP status codes from FamilySearch person and history downloads
            fsperson (dict): family search dictionary downloaded for the person id
            timestamp (int): the timestamp for the whole session
            fsperson_changes (dict): change history for person id
    """

    def __init__(
            self,
            personid,
            generation,
            referenceid,
            status_list,
            fsperson,
            timestamp,
            fsperson_changes):

        def get_list(momordad, parents):
            """ get dictionary keys with momordad from parents
                Args:
                    momordad (str): 'father' or 'mother'
                    parents (dict): {'abc': 'father', 'def': 'father', 'ghi': 'mother'}
                Return:
                    (list): ['abc', 'def'] or ['ghi']
            """
            mylist = []
            for parentkey, parentvalue in parents.items():
                if momordad == parentvalue:
                    mylist.append(parentkey)
            return json.dumps(mylist, sort_keys=True) # encoded, filtered, unique and sorted json list

        #
        # parameters
        self.personid = personid
        self.generation = generation
        self.referenceid = referenceid
        self.status_list = json.dumps(status_list)
        self.status = 'undefined'
        self.fsperson = json.dumps(fsperson)
        self.timestamp = timestamp
        if fsperson is not None:
            # FamilySearch.person.display
            disp = read_nested_dict(fsperson, "persons", 0, "display")
            self.name = read_nested_dict(disp, "name")
            self.gender = read_nested_dict(disp, "gender")
            self.born = read_nested_dict(disp, "birthDate")
            self.lifespan = read_nested_dict(disp, "lifespan")

            # FamilySearch.childAndParentsRelationships.person1(person2)
            parents = self.get_parents(fsperson)
            self.fatherids = get_list("father", parents)
            self.motherids = get_list("mother", parents)

            # FamilySearch.person.relationships(list) for person
            relationships = read_nested_dict(fsperson, "relationships")
            relationships_asc = sorted(relationships, key=lambda k: k['id'])
            self.relationships = json.dumps(relationships_asc)
        else:
            self.name = None
            self.gender = None
            self.born = None
            self.lifespan = None
            self.fatherids = []
            self.motherids = []
            self.relationships = None
        if fsperson_changes is not None:
            # FamilySearch change history(dict) for person
            self.last_modified = read_nested_dict(fsperson_changes, "updated")
        else:
            self.last_modified = None

    def get_parents(self, fsperson):
        """ read father(s) and mother(s) from family search person dictionary
            Args:
                fsperson (dict): family search dictionary downloaded for the person id
            Return:
                (dict):          {"abc": "father", "def": "father", "hgi": "mother"}
        """
        try:
            parents = {}
            if "childAndParentsRelationships" in fsperson:
                for rel in fsperson["childAndParentsRelationships"]:
                    child = rel["child"]["resourceId"] if "child" in rel else None
                    if child == self.personid:
                        father = rel["parent1"]["resourceId"] if "parent1" in rel else None
                        if father is not None:
                            parents[father] = 'father' # biological, adoptive, etc.
                        mother = rel["parent2"]["resourceId"] if "parent2" in rel else None
                        if mother is not None:
                            parents[mother] = 'mother' # biological, adoptive, etc.
            return parents
        except Exception as err:
            write_log(
                'error',
                "Exception(1): key '" +
                err.args[0] +
                "' not found in FS.childAndParentsRelationships.")
            return []

    def has_bad_requests(self):
        """ check for HTTP error code 429: too many requests
            Return:
                (bool): True = code 429 happened, False = not
        """
        return_code = False
        valid_codes = (200, 301, 404, 410, 429)
        status_list = json.loads(self.status_list)
        for code in status_list:
            if code not in valid_codes:
                write_log('error', 'Unexpected HTTP code: ' + str(code))
        #
        if 429 in status_list:
            write_log('error', 'HTTP error 429: too many requests')
            return_code = True  # breaks outer loop
        #
        return return_code

    def is_unreachable(self):
        """ check for HTTP error codes for: mergers, not found, and deletions
            Return:
                (bool): True = person object is unreachable, False = OK
        """
        status_list = json.loads(self.status_list)
        if 301 in status_list:
            write_log(
                'info',
                'Requested person (' +
                self.personid +
                ') merged into another person')
            return True
        elif 404 in status_list:
            write_log(
                'info',
                'Requested person (' +
                self.personid +
                ') not found.')
            return True
        elif 410 in status_list:
            write_log(
                'info',
                'Requested person (' +
                self.personid +
                ') has been deleted.')
            return True
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
        Note:
            This function needs to be (reason unknown) 'outside' of the Person object.
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
        write_log(
            'error',
            "Exception(2): index '" +
            err.args[0] +
            "' not found in FS.parents.")
        return None

# ----------


def write_log(level, text):
    """ write text to stderr, conditionally
        Args:
            level(str): 'info', 'error', or 'debug'
    """
    def wr(level, text):
        """ write text to stderr """
        log = "[%s] %s: %s\n" % (time.strftime(
            "%Y-%m-%d %H:%M:%S"), level.upper(), text)
        sys.stderr.write(log)

    if (level == 'debug'):
        if debug_app:
            wr(level, text)
    elif (level == 'error') or (level == 'info'):
        wr(level, text)
    else:
        wr('error', 'Bug detected in app.write_log: illegal level(' + level + ').')

# ----------


def get_person_object(person_id, generation, reference_id, timestamp, fs):
    """ download person data from the FamilySearch site
        Args:
            person_id (str): person id in family search
            generation (int): generation, starts at 0, ascending
            reference_id (str): reference peerson (generation 0)
            timestamp (int): timestamp for the whole session
            fs (Session): logged in session object
        Returns:
            (PersonObj)
    """
    fs_person = fs.get_person(person_id)
    fs_status = [fs.status_code]
    fs_change = fs.get_change_history_person(person_id)
    fs_status.append(fs.status_code)
    return PersonObj(
        person_id,
        generation,
        reference_id,
        fs_status,
        fs_person,
        timestamp,
        fs_change)

# ----------


def verify_data(reference_id, checklist):
    """ compare checklist with the persisted data
        Args:
            reference_id (str): the reference person who's ancestors are queried
            checklist (list): list of all persons (str) queried
    """
    db = dbm.Database()  # SQLlite database
    persons = db.get_persons(reference_id)
    for person in persons:
        pid = person['personid']
        if pid not in checklist:
            write_log(
                'error',
                'Found person ' +
                pid +
                ' in database, but not in FamilySearch (missing).')

# ----------


def checkmyancestors(args):
    """
    This is the heavy lifting part of the application, persisting FamilySearch data in a database.
    The database also contains created, updated, deleted metadata for all ancestors
    """
    now = datetime.now()
    timestamp = int(datetime.timestamp(now))
    debug_app = (args.debug == 'on')

    # objects
    db = dbm.Database()  # SQLlite database
    fs = sem.Session(args.username, args.password, timeout=10)  # FamilySearch
    if not fs.logged:
        write_log('info', "Failed to login as user: " + args.username)
        return
    write_log('info', "Successfully logged in as user: " + args.username)

    # reference_id
    reference_id = fs.fid
    if args.individual is not None:
        reference_id = args.individual

    # initialize loop
    checklist = []
    changes = []
    person_count = 0
    todolist = []
    todolist.append(
        {'personid': reference_id,
         'generation': 0,
         'referenceid': reference_id,
         'childid': 'undefined'})

    # loop thru all ancestors in the list
    while todolist:

        # get person data from FS
        todo = todolist.pop(0)
        person = get_person_object(
            todo['personid'],
            todo['generation'],
            todo['referenceid'],
            timestamp,
            fs)

        # check for circular references
        if (person.personid in checklist):
            write_log('info',
                'Circular reference encountered for person ID: '+person.personid+". Parent of: "+todo['childid']+".")
            if checklist.count(person.personid)>2:
                write_log('info', 'Circular reference counted more than twice. Stopped query.')
                break
        checklist.append(person.personid)

        # check lifespan
        if (person.lifespan[0:4].isdigit()):
            year = int(person.lifespan[0:4])
            if year < 1600:
                write_log('info', 'Reached time limit of 1600 A.D. Stopped query.')
                break # anything older than 1600 is speculation, not fact

        if db.check_person(person.personid, person.referenceid) == False:
            person.status = 'created'
        # check HTTP status codes
        if person.has_bad_requests():
            break
        if person.is_unreachable():
            person.status = 'deleted'

        # persist person to database
        changes = changes + db.persist_person(person)
        write_log('info',
                  'Generation: '+str(person.generation)+', '+
                  'Person: ID='+person.personid+', Name='+person.name+' ('+person.lifespan+'), '+
                  'Parent of '+todo['childid']+'.')
        person_count += 1

        # check person's father
        for fatherid in json.loads(person.fatherids):
            if ((args.type == 'bioline') or (args.type == 'patriline')):
                todolist.append(
                    {'personid': fatherid,
                     'generation': person.generation + 1,
                     'referenceid': reference_id,
                     'childid': person.personid})

        # check person's mother
        for motherid in json.loads(person.motherids):
            if ((args.type == 'bioline') or (args.type == 'matriline')):
                todolist.append(
                    {'personid': motherid,
                     'generation': person.generation + 1,
                     'referenceid': reference_id,
                     'childid': person.personid})

    verify_data(reference_id, checklist)
    db.persist_session(timestamp, reference_id, person_count, changes)
    write_log('info', 'End of query, '+str(len(checklist))+' persons found.')

# ----------


def main():
    """
        main: checkmyancestors/app.py
    """
    print('This module is not a script, but part of the checkmyancestors application.')


if __name__ == "__main__":
    main()
