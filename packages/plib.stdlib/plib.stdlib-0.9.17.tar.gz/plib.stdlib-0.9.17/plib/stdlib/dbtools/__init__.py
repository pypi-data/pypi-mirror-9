#!/usr/bin/env python
"""
Sub-Package STDLIB.DBTOOLS of Package PLIB
Copyright (C) 2008-2014 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package implements a simplified interface for
working with the Python DB API.
"""

import os
from collections import OrderedDict

from plib.stdlib.coll import typed_namedtuple
from plib.stdlib.decotools import cached_function

try:
    import yaml
except ImportError:
    yaml = None


def typestr(fieldtype):
    # Quick hack but it works
    return (
        'bool' if 'bool' in fieldtype else
        'int' if 'int' in fieldtype else
        'str'
    )


class DBInterface(object):
    """Make it easier to work with database.
    """
    
    param_strings = {
        'qmark': "?",
        'format': "%s"
    }
    
    conn_methods = ('commit', 'rollback')
    cursor_methods = ('execute', 'executemany', 'fetchone', 'fetchmany', 'fetchall')
    
    db_mod = None
    paramstr = ""  # non-supported paramstyle will raise exception on any SQL with params
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        if self.db_mod:
            self.paramstr = self.param_strings.get(self.db_mod.paramstyle, self.paramstr)
        
        self.conn = self._get_connection(*args, **kwargs)
        self.cursor = self.conn.cursor()
        
        for obj, methods in ((self.conn, self.conn_methods),
                             (self.cursor, self.cursor_methods)):
            for method in methods:
                setattr(self, method, getattr(obj, method))
    
    def __del__(self):
        self.close()
    
    def _get_connection(self, *args, **kwargs):
        raise NotImplementedError
    
    def _get_fieldspec(self, field):
        raise NotImplementedError
    
    def get_fieldspecs(self, fields):
        return ', '.join(
            self._get_fieldspec(field) for field in fields
        )
    
    tables_sql = None
    tables_index = None
    
    def get_tables(self):
        self.execute(self.tables_sql)
        return [row[self.tables_index] for row in self.fetchall()]
    
    db_structure = None
    
    @classmethod
    @cached_function
    def get_tablespecs(cls, tablename):
        return (
            cls.db_structure[tablename] if isinstance(tablename, str) else
            list(OrderedDict(
                (fieldspec, None)
                for table in tablename
                for fieldspec in cls.db_structure[table]
            ).iterkeys())
        )
    
    @classmethod
    @cached_function
    def get_fields(cls, tablename):
        return [fieldspec.split(' ')[0] for fieldspec in cls.get_tablespecs(tablename)]
    
    @classmethod
    @cached_function
    def get_fieldtypes(cls, tablename):
        return zip(
            cls.get_fields(tablename),
            [typestr(fieldspec.split(' ')[1]) for fieldspec in cls.get_tablespecs(tablename)]
        )
    
    @classmethod
    @cached_function
    def get_tuple(cls, tablename):
        return typed_namedtuple(
            tablename if isinstance(tablename, str) else '_'.join(tablename),
            ", ".join(
                "{0} {1}".format(fieldname, fieldtype)
                for fieldname, fieldtype in cls.get_fieldtypes(tablename)
            )
        )
    
    def clear_table(self, tablename, commit=True, verbose=True):
        if verbose:
            print "Dropping table {0}...".format(tablename)
        self.execute("DROP TABLE {0};".format(tablename))
        if commit:
            self.commit()
    
    def clear_tables(self, verbose=True):
        if verbose:
            print "Clearing tables..."
        for tablename in self.get_tables():
            self.clear_table(tablename, commit=False, verbose=verbose)
        self.commit()
        if verbose:
            print "Clear tables complete."
    
    def create_table(self, tablename, fields=None, commit=True, verbose=True):
        if fields is None:
            fields = self.db_structure[tablename]
        sql = "CREATE TABLE {0}({1});".format(
            tablename,
            self.get_fieldspecs(fields)
        )
        if verbose:
            print sql
        self.execute(sql)
        if commit:
            self.commit()
    
    def create_tables(self, clear=False, verbose=True):
        if clear:
            self.clear_tables()
        existing_tables = self.get_tables()
        if all(tablename in existing_tables for tablename in self.db_structure):
            if verbose:
                print "Tables already created."
            return None
        if any(tablename in existing_tables for tablename in self.db_structure):
            if verbose:
                print "Tables partially created, aborting!"
            return False
        if verbose:
            print "Creating tables..."
        for tablename, fields in self.db_structure.iteritems():
            self.create_table(tablename, fields, commit=False, verbose=verbose)
        self.commit()
        if verbose:
            print "Table creation complete."
        return True
    
    def _get_sql_values(self, values):
        return ", ".join(self.paramstr for _ in xrange(len(values)))
    
    def add_row(self, tablename, values, commit=True, verbose=True):
        sql_values = self._get_sql_values(values)
        sql = "INSERT INTO {0} VALUES({1});".format(
            tablename,
            sql_values
        )
        if verbose:
            print sql, values
        self.execute(sql, values)
        if commit:
            self.commit()
    
    def add_rows(self, tablename, valuelist, verbose=True):
        if verbose:
            print "Adding {0}...".format(tablename)
        for values in valuelist:
            self.add_row(tablename, values, commit=False, verbose=verbose)
        self.commit()
        if verbose:
            print "{0} added.".format(tablename.capitalize())
    
    def _get_sql_where(self, keymap):
        return (
            " AND ".join("{0}={1}".format(field, self.paramstr) for field in keymap.iterkeys()),
            tuple(keymap.itervalues())
        )
    
    def _get_sql_set(self, valuemap):
        return (
            ", ".join("{0}={1}".format(field, self.paramstr) for field in valuemap.iterkeys()),
            tuple(valuemap.itervalues())
        )
    
    def update_row(self, tablename, keymap, valuemap, commit=True, verbose=True):
        if not (keymap and valuemap):
            return  # makes it easier to feed value sequences to update_rows
        sql_where, keys = self._get_sql_where(keymap)
        sql_set, values = self._get_sql_set(valuemap)
        sql = "UPDATE {0} SET {1} WHERE {2};".format(
            tablename,
            sql_set,
            sql_where
        )
        args = values + keys
        if verbose:
            print sql, args
        self.execute(sql, args)
        if commit:
            self.commit()
    
    def update_rows(self, tablename, values, verbose=True):
        if verbose:
            print "Updating {0}...".format(tablename)
        for keymap, valuemap in values:
            self.update_row(tablename, keymap, valuemap, commit=False, verbose=verbose)
        self.commit()
        if verbose:
            print "{0} updated.".format(tablename.capitalize())
    
    def _get_tablespec(self, tablename, include_nomatch):
        return (
            tablename if isinstance(tablename, str) else
            # assume tablename is iterable
            " {0} JOIN ".format("OUTER" if include_nomatch else "NATURAL").join(tablename)
        )
    
    def query(self, tablename, keymap=None, include_nomatch=False, verbose=True):
        if keymap:
            sql_where, keys = self._get_sql_where(keymap)
        if verbose:
            print "Querying {0}...".format(tablename)
        sql = "SELECT * FROM {0}{1};".format(
            self._get_tablespec(tablename, include_nomatch),
            " WHERE {0}".format(sql_where) if keymap else ""
        )
        if verbose:
            if keymap:
                print sql, keys
            else:
                print sql
        if keymap:
            self.execute(sql, keys)
        else:
            self.execute(sql)
        t = self.get_tuple(tablename)
        return [t(*row) for row in self.fetchall()]
    
    def match(self, tablename, keymap=None, include_nomatch=False, raise_mismatch=False, verbose=True):
        rows = self.query(tablename, keymap, include_nomatch=include_nomatch, verbose=verbose)
        if len(rows) == 1:
            return rows[0]
        if raise_mismatch:
            raise RuntimeError("{0} row matching keys: {1}".format(
                "More than one" if rows else "No",
                repr(keymap)
            ))
    
    def dump_table(self, tablename, as_dict=False):
        result = self.query(tablename)
        if as_dict:
            fields = self.get_fields(tablename)
            return [
                dict(izip(fields, row))
                for row in result
            ]
        return result
    
    def dump(self, as_dict=False):
        return dict(
            (tablename, self.dump_table(tablename, as_dict=as_dict))
            for tablename in self.get_tables()
        )


DB_SQLITE3 = 1
DB_MYSQL = 2


def get_db_interface_class(dbname, dbtype, structure, params):
    if dbtype is DB_SQLITE3:
        from plib.stdlib.dbtools.sqlite import SQLite3DBInterface
        intf_class = SQLite3DBInterface
    elif dbtype is DB_MYSQL:
        from plib.stdlib.dbtools.mysql import MySQLDBInterface
        intf_class = MySQLDBInterface
    else:
        raise RuntimeError("Invalid database type: {0}".format(repr(dbtype)))
    
    if isinstance(structure, basestring):
        if yaml:
            structure = yaml.load(structure)
        else:
            raise RuntimeError("Database structure definition must be a dictionary.")
    
    return type(intf_class)(
        '{0}DBInterface'.format(dbname) if dbname else intf_class.__name__,
        (intf_class,),
        dict(
            db_structure=structure,
            **(params or {})
        )
    )


def get_db_interface_args(dbname, dbtype, argpath, kwds):
    kwargs = {}
    if dbtype is DB_SQLITE3:
        args = (os.path.join(argpath, "{0}.db".format(dbname.lower())),)
    elif dbtype is DB_MYSQL:
        args = ()
        kwargs.update(
            (kwds or {}),
            use_unicode=True,
            charset='utf8'  # no hyphen for MySQL, unlike Python, HTML, etc., etc... :p
        )
    else:
        raise RuntimeError("Invalid database type: {0}".format(repr(dbtype)))
    return args, kwargs


def get_db_interface(dbname, dbtype, structure, params, argpath, kwds):
    klass = get_db_interface_class(dbname, dbtype, structure, params)
    args, kwargs = get_db_interface_args(dbname, dbtype, argpath, kwds)
    return klass(*args, **kwargs)
