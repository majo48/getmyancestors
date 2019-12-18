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
from checkmyancestors import databasemodule as dbm
from checkmyancestors import sessionmodule as sem
import json
import sys


class PersonObj:
    """ person object in this application
        Args:
            pid (str):  person id
            gen (int):  generation relative to reference person
            fsperson (dict): family search dictionary downloaded for the person id
    """

    def __init__(self, pid, gen, fsperson):
        # parameters
        self.pid = pid
        self.generation = gen
        self.fsperson = json.dumps(fsperson)
        # FamilySearch
        disp = read_nested_dict(fsperson, "persons", 0, "display")
        self.name = read_nested_dict(disp, "name")
        self.gender = read_nested_dict(disp, "gender")
        self.born = read_nested_dict(disp, "birthDate")
        self.lifespan = read_nested_dict(disp, "lifespan")
        parents = self.get_parents(pid, fsperson)
        self.father = parents["father"]
        self.mother = parents["mother"]

    def get_parents(self, pid, fsperson):
        """ read father and mother from family search person dictionary
            Args:
                pid (str):       person id
                fsperson (dict): family search dictionary downloaded for the person id
        """
        try:
            if "childAndParentsRelationships" in fsperson:
                for rel in fsperson["childAndParentsRelationships"]:
                    father = rel["parent1"]["resourceId"] if "parent1" in rel else None
                    mother = rel["parent2"]["resourceId"] if "parent2" in rel else None
                    child = rel["child"]["resourceId"] if "child" in rel else None
                    if child == pid:
                        return {"father": father, "mother": mother}
            return {"father": None, "mother": None}
        except Exception as err:
            print(sys.exc_info()[0], "Exception(1): key '"+err.args[0]+"' not found in FS.childAndParentsRelationships.")
            return {"father": None, "mother": None}

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
        print(sys.exc_info()[0], "Exception(2): index '"+err.args[0]+"' not found in FS.parents.")
        return None

# ----------


def checkmyancestors(args):
    """
    This is the heavy lifting part of the application, persisting FamilySearch data in a database.
    The database also contains created, updated, deleted metadata for all ancestors
    Returns:

    """
    db = dbm.Database()
    fs = sem.Session(args.username, args.password, timeout=10)
    reference_id = fs.fid
    generation = 0
    #
    # create a person object
    po = PersonObj(reference_id, generation, fs.get_person(reference_id))
    dummy = 'stop'  # todo continue here

# ----------


def main():
    """
        main: checkmyancestors/app.py
    """
    print('main: checkmyancestors/app.py')


if __name__ == "__main__":
    main()
