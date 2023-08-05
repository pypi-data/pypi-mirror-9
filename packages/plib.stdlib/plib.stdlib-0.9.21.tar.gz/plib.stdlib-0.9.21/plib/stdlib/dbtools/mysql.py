#!/usr/bin/env python
"""
Module MYSQL -- MySQL Database Interface
Sub-Package STDLIB.DBTOOLS of Package PLIB
Copyright (C) 2008-2014 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements the MySQL interface built with
PLIB.STDLIB.DBTOOLS.
"""

import MySQLdb

from plib.stdlib.decotools import cached_function
from plib.stdlib.dbtools import DBInterface


class MySQLDBInterface(DBInterface):
    
    cursor_methods = DBInterface.cursor_methods + ('close',)
    
    db_mod = MySQLdb
    
    def _get_connection(self, *args, **kwargs):
        return MySQLdb.connect(**kwargs)
    
    def _get_fieldspec(self, field):
        # Fieldspecs are already in MySQL format
        return field
    
    tables_sql = "SHOW TABLES;"
    tables_index = 0
    
    fields_sql = "SHOW FIELDS IN {0};"
    fields_iter = True
    
    def _get_fieldvalue(self, row):
        # TODO: add field type and canonicalize
        return row[0]  # type is row[1] in datatype(bytes) format
