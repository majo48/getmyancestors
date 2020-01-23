#!/usr/bin/env python3
# coding: utf-8
"""
   sessionmodule.py - login to FamilySearch and check current ancestors
   Acknowledgement: copied (in part and upgraded) from getmyancestors.py

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


# global import
import os
import time
import requests
import unittest
import json
from checkmyancestors import app
from checkmyancestors import credentials


class Session:
    """ Create a FamilySearch session
        :param username and password: valid FamilySearch credentials
        :param timeout: time before retry a request
    """

    def __init__(self, username, password, timeout=60):
        self.username = username
        self.password = password
        self.timeout = timeout
        self.fid = self.lang = self.display_name = None
        self.counter = 0
        self.logged = self.login()
        self.status_code = 200

    def login(self):
        """ retrieve FamilySearch session ID
            (https://familysearch.org/developers/docs/guides/oauth2)
        """
        while True:
            try:
                url = "https://www.familysearch.org/auth/familysearch/login"
                app.write_log('debug', "Downloading: " + url)
                r = requests.get(
                    url,
                    params={
                        "ldsauth": False},
                    allow_redirects=False)
                url = r.headers["Location"]
                app.write_log('debug', "Downloading: " + url)
                r = requests.get(url, allow_redirects=False)
                idx = r.text.index('name="params" value="')
                span = r.text[idx + 21:].index('"')
                params = r.text[idx + 21: idx + 21 + span]

                url = "https://ident.familysearch.org/cis-web/oauth2/v3/authorization"
                app.write_log('debug', "Downloading: " + url)
                r = requests.post(
                    url,
                    data={
                        "params": params,
                        "userName": self.username,
                        "password": self.password},
                    allow_redirects=False,
                )

                if "The username or password was incorrect" in r.text:
                    app.write_log(
                        'error', "The username or password was incorrect")
                    return False

                if "Invalid Oauth2 Request" in r.text:
                    app.write_log('error', "Invalid Oauth2 Request")
                    time.sleep(self.timeout)
                    continue

                url = r.headers["Location"]
                app.write_log('debug', "Downloading: " + url)
                r = requests.get(url, allow_redirects=False)
                self.fssessionid = r.cookies["fssessionid"]
            except requests.exceptions.ReadTimeout:
                app.write_log('debug', "Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                app.write_log('debug', "Connection aborted")
                time.sleep(self.timeout)
                continue
            except requests.exceptions.HTTPError:
                app.write_log('debug', "HTTPError")
                time.sleep(self.timeout)
                continue
            except KeyError:
                app.write_log('debug', "KeyError")
                time.sleep(self.timeout)
                continue
            except ValueError:
                app.write_log('debug', "ValueError")
                time.sleep(self.timeout)
                continue
            app.write_log(
                'debug',
                "FamilySearch session id: " +
                self.fssessionid)
            self.set_current()
            return True

    def get_url(self, url, fsaccept="application/json"):
        """
            retrieve JSON structure from a FamilySearch URL
        """
        self.counter += 1
        loop_counter = 0
        while loop_counter <= 3:
            loop_counter += 1
            try:
                app.write_log('debug', "Downloading: " + url)
                r = requests.get(
                    "https://familysearch.org" + url,
                    headers={"Accept": fsaccept},
                    cookies={"fssessionid": self.fssessionid},
                    timeout=self.timeout,
                )
            except requests.exceptions.ReadTimeout:
                app.write_log('debug', "Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                app.write_log('debug', "Connection aborted")
                time.sleep(self.timeout)
                continue
            app.write_log('debug', "Status code: %s" % r.status_code)
            self.status_code = r.status_code
            if r.status_code == 204:
                # The request was successful but nothing was available to
                # return.
                return None
            if r.status_code in {404, 405, 406, 410, 429, 500, 503, 504}:
                # 404: A resource was requested that does not exist.
                # 405: The request was not understood by the networking and routing infrastructure.
                # 406: An invalid content type is being used in the Accept header.
                # 410: The resource you are requesting has been deleted.
                # 429: Too many requests, the user has used too much processing time recently.
                # 500: Internal Server Error.
                # 503: Service Unavailable.
                # 504: Gateway Timeout.
                app.write_log(
                    'debug',
                    "WARNING: code " +
                    r.status_code +
                    ", " +
                    url)
                return None
            if r.status_code == 401:
                # The user is not properly authenticated.
                self.login()
                continue
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                app.write_log('debug', "HTTPError")
                if r.status_code == 403:
                    # A resource was requested that the user does not have
                    # permission to access.
                    app.write_log(
                        'debug',
                        "WARNING: code " +
                        r.status_code +
                        ", " +
                        url)
                    return None
                time.sleep(self.timeout)
                continue
            try:
                return r.json()
            except Exception as e:
                # 420: Methode failure
                self.status_code = 420
                app.write_log(
                    'error', "WARNING: corrupted file from %s, error: %s" %
                    (url, e))
                return None
        return None

    def set_current(self):
        """ retrieve FamilySearch current user ID, name and language """
        url = "/platform/users/current.json"
        data = self.get_url(url)
        if data:
            self.fid = data["users"][0]["personId"]
            self.lang = data["users"][0]["preferredLanguage"]
            self.display_name = data["users"][0]["displayName"]

    def get_person(self, person_id):
        """ get person from FamilySearch """
        url = "/platform/tree/persons/%s" % person_id
        return self.get_url(url, "application/x-gedcomx-v1+json")

    def get_change_history_person(self, person_id):
        """ get change history from FamilySearch """
        url = "/platform/tree/persons/%s/changes" % person_id
        return self.get_url(url, "application/x-gedcomx-atom+json")

    def _(self, string):
        """ translate a string into user's language
            TODO add translation file(s) in gettext format
        """
        return string


class TestSessionModule(unittest.TestCase):
    fs = None
    person = None

    def setUp(self):
        pass

    def test_1_credentials(self):
        # checks for the existence of file checkmyancestors/credentials.py
        self.assertIsInstance(
            credentials.username,
            str,
            "Username shall be defined.")
        self.assertIsInstance(
            credentials.password,
            str,
            "Password shall be defined")

    def test_2_login(self):
        # check for successfull login
        self.__class__.fs = Session(
            username=credentials.username,
            password=credentials.password,
            timeout=10)
        self.assertIsInstance(self.__class__.fs, Session)
        self.assertTrue(self.__class__.fs.logged, "Login failed.")

    def test_3_get_person(self):
        # check for download of Thomas Alva Edison
        person = self.__class__.fs.get_person('LZ2Q-W96')
        self.assertIn(
            'description',
            person,
            'Dictionary shall contain "description" element.')
        self.assertEqual(person['description'], '#SD-LZ2Q-W96')
        self.__class__.person = person

    def test_4_display(self):
        # check the display part of person data
        person = self.__class__.person
        try:
            display = person['persons'][0]['display']
        except BaseException:
            self.assertTrue(
                False, 'Missing "display" element in "person" object.')
            return
        self.assertIn(
            'name',
            display,
            'The "display" element shall contain the "name" attribute.')
        self.assertEqual(display['name'], 'Thomas Alva Edison')

    def test_5_relationships(self):
        # check the relationships part of person data
        person = self.__class__.person
        self.assertIn(
            'childAndParentsRelationships',
            person,
            'The "person" object shall contain the "childAndParentsRelationships" attribute.')
        try:
            for relation in person["childAndParentsRelationships"]:
                self.assertIn(
                    'parent1',
                    relation,
                    'Relationship shall contain "parent1" element.')
                self.assertIn(
                    'parent2',
                    relation,
                    'Relationship shall contain "parent2" element.')
                self.assertIn(
                    'child',
                    relation,
                    'Relationship shall contain "child" element.')
        except BaseException:
            self.assertTrue(
                False, 'Missing "relationships" element(s) in "person" object.')


if __name__ == "__main__":
    unittest.main(failfast=True)
