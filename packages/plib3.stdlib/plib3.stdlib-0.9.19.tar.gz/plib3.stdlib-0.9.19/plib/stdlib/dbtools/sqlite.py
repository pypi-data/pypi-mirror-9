#!/usr/bin/env python3
"""
Module SQLITE -- SQLite 3 Database Interface
Sub-Package STDLIB.DBTOOLS of Package PLIB3
Copyright (C) 2008-2014 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements the SQLite 3 interface built with
PLIB.STDLIB.DBTOOLS.
"""

import sqlite3

from plib.stdlib.dbtools import DBInterface


DB_FIELDTYPES = {
    'varchar': 'TEXT',
    'text': 'TEXT',
    'tinyint': 'INT',
    'smallint': 'INT',
    'int': 'INT',
    'bool': 'INT'
}


class SQLite3DBInterface(DBInterface):
    
    conn_methods = DBInterface.conn_methods + ('close',)
    
    db_mod = sqlite3
    
    def _get_connection(self, *args, **kwargs):
        return sqlite3.connect(*args)
    
    def _get_fieldspec(self, field):
        fieldname, fieldtype = field.split(' ', 1)
        if '(' in fieldtype:
            # Remove the length spec for varchars to simplify lookup
            fieldtype, _ = fieldtype.split('(', 1)
        return "{0} {1}".format(fieldname, DB_FIELDTYPES[fieldtype])
    
    tables_sql = "SELECT * FROM sqlite_master WHERE type='table';"
    tables_index = 1
