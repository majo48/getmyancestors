getmyancestors (forked)
==============
- This repository has been forked from project **Linekio/getmyanscestors** version Aug 26, 2019 (commit f32eb13).
- Change Nr.1 : Code fixes for bugs found during analysis of the existing software.
  - Max persons changed from 200 to 500
  - API change(?) for "childAndParentsRelationships": replace father with parent1, mother with parent2
  - Tested on a MacBook OSX 10.11.6
- Change Nr.2 (pending): file system bug, files not closed when running in cli mode.
- Planned: 
  - Lists (database) of ancestors, including the last change dates of the source records.
  - Comparison of lists enables users to detect new and/or deleted ancestors.
  - 3 types of ancestors:
    - Patriline ("father line") is a person's father, and additional ancestors, as traced only through males. 
    - Matriline ("mother line") is a person's mother, and additional ancestors, as traced only through females.
    - Bioline ("biological line") is a persons father and mother, and additional ancestors (traced through males and females).

getmyancestors
==============

getmyancestors.py is a python3 script that downloads family trees in GEDCOM format from FamilySearch.

This program is now in production phase, but bugs might still be present. Features will be added on request. It is provided as is.

The project is maintained at https://github.com/Linekio/getmyancestors. Visit here for the latest version and more information.

This script requires python3, the requests module, and the babelfish module to work. To install the modules, run in your terminal:

For requests:

"python3 -m pip install requests" (or "python3 -m pip install --user requests" if you don't have admin rights on your machine).

For babelfish:

"python3 -m pip install babelfish" (or "python3 -m pip install --user babelfish" if you don't have admin rights on your machine).

This script requires python 3.4 (or higher) to run due to some novel features in the argparse and asyncio modules (https://docs.python.org/3/whatsnew/3.4.html)

The graphical interface requires tkinter (https://docs.python.org/3/library/tkinter.html) and diskcache.

To download the script, click on the green button "Clone or download" on the top of this page and then click on "Download ZIP".

Current version was updated on November 11th 2018.


How to use
==========

With graphical user interface:

```
python3 fstogedcom.py
```

Command line examples:

Download four generations of ancestors for the main individual in your tree and output gedcom on stdout (will prompt for username and password):

```
python3 getmyancestors.py
```

Download four generations of ancestors and output gedcom to a file while generating a verbode stderr (will prompt for username and password):

```
python3 getmyancestors.py -o out.ged -v
```

Download four generations of ancestors for individual LF7T-Y4C and generate a verbose log file:

```
python3 getmyancestors.py -u username -p password -i LF7T-Y4C -o out.ged -l out.log -v
```

Download six generations of ancestors for individual LF7T-Y4C and generate a verbose log file:

```
python3 getmyancestors.py -a 6 -u username -p password -i LF7T-Y4C -o out.ged -l out.log -v
```

Download four generations of ancestors for individual LF7T-Y4C including all their children and their children spouses:

```
python3 getmyancestors.py -d 1 -m -u username -p password -i LF7T-Y4C -o out.ged
```

Download six generations of ancestors for individuals L4S5-9X4 and LHWG-18F including all their children, grandchildren and their spouses:

```
python3 getmyancestors.py -a 6 -d 2 -m -u username -p password -i L4S5-9X4 LHWG-18F -o out.ged
```

Download four generations of ancestors for individual LF7T-Y4C including LDS ordinances (need LDS account)

```
python3 getmyancestors.py -c -u username -p password -i LF7T-Y4C -o out.ged
```
Support
=======

Send questions, suggestions, or feature requests to benoitfontaine.ba@gmail.com or giulio.genovese@gmail.com, or open an Issue at https://github.com/Linekio/getmyancestors/issues

Donation
========

If this project help you, you can give me a tip :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=98X3CY93XTAYJ)
