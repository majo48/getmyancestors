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
import sys
import time
import requests
from checkmyancestors import app

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


    def login(self):
        """ retrieve FamilySearch session ID
            (https://familysearch.org/developers/docs/guides/oauth2)
        """
        while True:
            try:
                url = "https://www.familysearch.org/auth/familysearch/login"
                app.write_log("Downloading: " + url)
                r = requests.get(url, params={"ldsauth": False}, allow_redirects=False)
                url = r.headers["Location"]
                app.write_log("Downloading: " + url)
                r = requests.get(url, allow_redirects=False)
                idx = r.text.index('name="params" value="')
                span = r.text[idx + 21 :].index('"')
                params = r.text[idx + 21 : idx + 21 + span]

                url = "https://ident.familysearch.org/cis-web/oauth2/v3/authorization"
                app.write_log("Downloading: " + url)
                r = requests.post(
                    url,
                    data={"params": params, "userName": self.username, "password": self.password},
                    allow_redirects=False,
                )

                if "The username or password was incorrect" in r.text:
                    app.write_log("The username or password was incorrect")
                    return False

                if "Invalid Oauth2 Request" in r.text:
                    app.write_log("Invalid Oauth2 Request")
                    time.sleep(self.timeout)
                    continue

                url = r.headers["Location"]
                app.write_log("Downloading: " + url)
                r = requests.get(url, allow_redirects=False)
                self.fssessionid = r.cookies["fssessionid"]
            except requests.exceptions.ReadTimeout:
                app.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                app.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            except requests.exceptions.HTTPError:
                app.write_log("HTTPError")
                time.sleep(self.timeout)
                continue
            except KeyError:
                app.write_log("KeyError")
                time.sleep(self.timeout)
                continue
            except ValueError:
                app.write_log("ValueError")
                time.sleep(self.timeout)
                continue
            app.write_log("FamilySearch session id: " + self.fssessionid)
            self.set_current()
            return True

    def get_url(self, url):
        """
            retrieve JSON structure from a FamilySearch URL
        """
        self.counter += 1
        while True:
            try:
                app.write_log("Downloading: " + url)
                r = requests.get(
                    "https://familysearch.org" + url,
                    headers={"Accept": "application/x-gedcomx-v1+json"},
                    cookies={"fssessionid": self.fssessionid},
                    timeout=self.timeout,
                )
            except requests.exceptions.ReadTimeout:
                app.write_log("Read timed out")
                continue
            except requests.exceptions.ConnectionError:
                app.write_log("Connection aborted")
                time.sleep(self.timeout)
                continue
            app.write_log("Status code: %s" % r.status_code)
            if r.status_code == 204:
                return None
            if r.status_code in {404, 405, 410, 500}:
                app.write_log("WARNING: " + url)
                return None
            if r.status_code == 401:
                self.login()
                continue
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                app.write_log("HTTPError")
                if r.status_code == 403:
                    if (
                        "message" in r.json()["errors"][0]
                        and r.json()["errors"][0]["message"] == "Unable to get ordinances."
                    ):
                        app.write_log(
                            "Unable to get ordinances. "
                            "Try with an LDS account or without option -c."
                        )
                        return "error"
                    app.write_log(
                        "WARNING: code 403 from %s %s"
                        % (url, r.json()["errors"][0]["message"] or "")
                    )
                    return None
                time.sleep(self.timeout)
                continue
            try:
                return r.json()
            except Exception as e:
                app.write_log("WARNING: corrupted file from %s, error: %s" % (url, e))
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
        return self.get_url(url)

    def _(self, string):
        """ translate a string into user's language
            TODO add translation file(s) in gettext format
        """
        return string


def main():
    """ main: databasemodule.py """
    print('module: databasemodule.py')

if __name__ == "__main__":
            main()