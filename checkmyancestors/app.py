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


class PersonObj:
    """ person object in this application
        Args:
            pid (str):  person id
            gen (int):  generation relative to reference person
            json (str): json string downloaded for the person id
    """

    def __init__(self, pid, gen, json):
        # parameters
        self.pid = pid
        self.generation = gen
        self.json = json
        # FamilySearch
        disp = exjson(self.json, "persons", 0, "display")
        self.name = exjson(disp, "name")
        self.gender = exjson( disp, "gender")
        self.born = exjson( disp, "birthDate")
        self.lifespan = exjson( disp, "lifespan")
        self.father = None #todo another method
        self.mother = None #todo another method
        dummy = 'stop'


def exjson(jsn: dict, *args):
    """
        Extract the arguments part from the json data from FamilySearch.
        If missing or changed indexes to the data, the value persisted is None.
        Args:
            jsn (dict): dictionary, complex, nested
            *args (tuple): sequence of indexes in above dictionary
        Returns:
            value (str, int, list, or dict)
    """
    try:
        x = jsn.copy()
        for y in args:
            if isinstance(x, dict):
                x = x.get(y)
            elif isinstance(x, list):
                x = x.pop(y)
            else:
                return None
        return x
    except Exception as err:
        print(err)
        return None


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
    po = PersonObj(reference_id, generation, fs.get_person(reference_id))
    dummy = 'stop'  # todo continue here


def main():
    """
        main: checkmyancestors/app.py
    """
    print('main: checkmyancestors/app.py')


if __name__ == "__main__":
    main()
