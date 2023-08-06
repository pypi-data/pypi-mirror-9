#!/usr/bin/env python2.7

import sqlite3, json

def install_json_converter():
    """ Installs a json object converter into the sqlite3 module for
        quick type conversions.
    """

    sqlite3.register_converter("json", __convert_json)

def __convert_json(string):
    """ Converts a string into JSON format.  If the conversion fails,
        returns None.
    """

    try:
        return json.loads(string)
    except:
        return None
