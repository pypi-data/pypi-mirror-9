#!/usr/bin/env python3
"""
Sub-Package STDLIB.DBTOOLS of Package PLIB3
Copyright (C) 2008-2014 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package implements a simplified interface for
working with the Python DB API.
"""

import os
from collections import OrderedDict
from functools import partial

from plib.stdlib.coll import namedtuple, typed_namedtuple
from plib.stdlib.decotools import cached_function

try:
    import yaml
except ImportError:
    yaml = None


def maybe(t, null_values=None, null_fields=None,
          null_default_values=(None,), null_default_fields={bool: False, int: 0, str: ""}):
    
    def _f(v):
        if v in (null_values or null_default_values):
            return (null_fields or null_default_fields)[t]
        return t(v)
    _f.__name__ = 'maybe_{0}'.format(t.__name__)
    return _f


def smart_type(fieldtype, null_values=None, null_fields=None):
    return maybe(
        bool if 'bool' in fieldtype else
        int if 'int' in fieldtype else
        str,
        null_values, null_fields
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
    
    fields_sql = None
    fields_iter = None
    
    def _get_fieldvalue(self, row):
        raise NotImplementedError
    
    def _get_tablename(self, row):
        raise NotImplementedError
    
    def _get_fieldvalues(self, row):
        raise NotImplementedError
    
    def get_fieldmap(self):
        if self.fields_iter:
            result = {}
            for tablename in self.get_tables():
                sql = self.fields_sql.format(tablename)
                self.execute(sql)
                rows = self.fetchall()
                result[tablename] = [self._get_fieldvalue(row) for row in rows]
        else:
            sql = self.fields_sql
            self.execute(sql)
            rows = self.fetchall()
            result = {self._get_tablename(row): self._get_fieldvalues(row) for row in rows}
        return result
    
    def get_map_fields(self, tablename):
        fmap = self.get_fieldmap()
        return (
            fmap[tablename] if isinstance(tablename, str) else
                list(OrderedDict(
                (fieldname, None)
                for table in tablename
                for fieldname in fmap[table]
            ).iterkeys())
        )
    
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
        return [fieldspec.split(' ')[1] for fieldspec in cls.get_tablespecs(tablename)]
    
    null_values = null_fields = None
    
    @classmethod
    @cached_function
    def get_tuple(cls, tablename, untyped=False):
        tuple_name = tablename if isinstance(tablename, str) else '_'.join(tablename)
        if untyped:
            return namedtuple(tuple_name, tuple(cls.get_fields(tablename)))
        return typed_namedtuple(
            tuple_name,
            tuple(
                (fieldname, smart_type(fieldtype, cls.null_values, cls.null_fields))
                for fieldname, fieldtype in zip(cls.get_fields(tablename), cls.get_fieldtypes(tablename))
            )
        )
    
    def clear_table(self, tablename, commit=True, verbose=True):
        if verbose:
            print("Dropping table {0}...".format(tablename))
        self.execute("DROP TABLE {0};".format(tablename))
        if commit:
            self.commit()
    
    def clear_tables(self, commit=True, verbose=True):
        if verbose:
            print("Clearing tables...")
        for tablename in self.get_tables():
            self.clear_table(tablename, commit=False, verbose=verbose)
        if commit:
            self.commit()
        if verbose:
            print("Clear tables complete.")
    
    def create_table(self, tablename, fields=None, commit=True, verbose=True):
        if fields is None:
            fields = self.db_structure[tablename]
        sql = "CREATE TABLE {0}({1});".format(
            tablename,
            self.get_fieldspecs(fields)
        )
        if verbose:
            print(sql)
        self.execute(sql)
        if commit:
            self.commit()
    
    def create_tables(self, clear=False, commit=True, verbose=True):
        if clear:
            self.clear_tables()
        existing_tables = self.get_tables()
        if all(tablename in existing_tables for tablename in self.db_structure):
            if verbose:
                print("Tables already created.")
            return None
        if any(tablename in existing_tables for tablename in self.db_structure):
            if verbose:
                print("Tables partially created, aborting!")
            return False
        if verbose:
            print("Creating tables...")
        for tablename, fields in self.db_structure.items():
            self.create_table(tablename, fields, commit=False, verbose=verbose)
        if commit:
            self.commit()
        if verbose:
            print("Table creation complete.")
        return True
    
    def _get_sql_values(self, values):
        return ", ".join(self.paramstr for _ in range(len(values)))
    
    def add_row(self, tablename, values, commit=True, verbose=True):
        sql_values = self._get_sql_values(values)
        sql = "INSERT INTO {0} VALUES({1});".format(
            tablename,
            sql_values
        )
        if verbose:
            print(sql, values)
        self.execute(sql, values)
        if commit:
            self.commit()
    
    def add_rows(self, tablename, valuelist, commit=True, verbose=True):
        if verbose:
            print("Adding {0}...".format(tablename))
        for values in valuelist:
            self.add_row(tablename, values, commit=False, verbose=verbose)
        if commit:
            self.commit()
        if verbose:
            print("{0} added.".format(tablename.capitalize()))
    
    def _get_sql_where(self, keymap):
        return (
            " AND ".join("{0}={1}".format(field, self.paramstr) for field in keymap.keys()),
            tuple(keymap.values())
        )
    
    def _get_sql_set(self, valuemap):
        return (
            ", ".join("{0}={1}".format(field, self.paramstr) for field in valuemap.keys()),
            tuple(valuemap.values())
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
            print(sql, args)
        self.execute(sql, args)
        if commit:
            self.commit()
    
    def update_rows(self, tablename, values, commit=True, verbose=True):
        if verbose:
            print("Updating {0}...".format(tablename))
        for keymap, valuemap in values:
            self.update_row(tablename, keymap, valuemap, commit=False, verbose=verbose)
        if commit:
            self.commit()
        if verbose:
            print("{0} updated.".format(tablename.capitalize()))
    
    def _get_tablespec(self, tablename, include_nomatch):
        return (
            tablename if isinstance(tablename, str) else
            # assume tablename is iterable
            " {0} JOIN ".format("NATURAL LEFT" if include_nomatch else "NATURAL").join(tablename)
        )
    
    def get_rows(self, tablename, keymap=None, fields=None, use_structure=True, include_nomatch=False, verbose=True):
        if keymap:
            sql_where, keys = self._get_sql_where(keymap)
        if verbose:
            print("Querying {0}...".format(tablename))
        sql = "SELECT {0} FROM {1}{2};".format(
            fields if isinstance(fields, basestring) else ", ".join(
                fields or (self.get_fields if use_structure else self.get_map_fields)(tablename)
            ),
            self._get_tablespec(tablename, include_nomatch),
            " WHERE {0}".format(sql_where) if keymap else ""
        )
        if verbose:
            if keymap:
                print(sql, keys)
            else:
                print(sql)
        if keymap:
            self.execute(sql, keys)
        else:
            self.execute(sql)
        return self.fetchall()
    
    def query(self, tablename, keymap=None, include_nomatch=False, untyped=False, verbose=True):
        rows = self.get_rows(tablename, keymap, include_nomatch=include_nomatch, verbose=verbose)
        t = self.get_tuple(tablename, untyped=untyped)
        return [t(*row) for row in rows]
    
    def match(self, tablename, keymap=None, include_nomatch=False, raise_mismatch=False, untyped=False, verbose=True):
        rows = self.query(tablename, keymap, include_nomatch=include_nomatch, untyped=untyped, verbose=verbose)
        if len(rows) == 1:
            return rows[0]
        if raise_mismatch:
            raise RuntimeError("{0} row matching keys: {1}".format(
                "More than one" if rows else "No",
                repr(keymap)
            ))
    
    def delete_rows(self, tablename, keymap=None, commit=True, verbose=True):
        if keymap:
            sql_where, keys = self._get_sql_where(keymap)
        if verbose:
            print("Deleting from {0}...".format(tablename))
        sql = "DELETE FROM {0}{1};".format(
            tablename,
            " WHERE {0}".format(sql_where) if keymap else ""
        )
        if verbose:
            if keymap:
                print(sql, keys)
            else:
                print(sql)
        if keymap:
            self.execute(sql, keys)
        else:
            self.execute(sql)
        if commit:
            self.commit()
    
    def dump_table(self, tablename, use_structure=True, as_dict=False, verbose=True):
        if verbose:
            print("Dumping", tablename)
        result = self.get_rows(tablename, use_structure=use_structure)
        if as_dict:
            fields = (self.get_fields if use_structure else self.get_map_fields)(tablename)
            return [
                dict(zip(fields, row))
                for row in result
            ]
        return result
    
    def _get_included_tables(self, tables, exclude_tables):
        if exclude_tables and not tables:
            tables = self.get_tables()
            for t in exclude_tables:
                tables.remove(t)
        return tables
    
    def dump(self, tables=None, exclude_tables=None, use_structure=True, as_dict=False, verbose=True):
        tables = self._get_included_tables(tables, exclude_tables)
        return dict(
            (tablename, self.dump_table(tablename, use_structure=use_structure, as_dict=as_dict, verbose=verbose))
            for tablename in (tables or self.get_tables())
        )
    
    def load_table(self, tablename, rows, as_dict=False, clear=True, verbose=True):
        if clear:
            self.clear_table(tablename, commit=False, verbose=verbose)
            self.create_table(tablename, commit=False, verbose=verbose)
            self.commit()
        if verbose:
            print("Loading", tablename)
        t = self.get_tuple(tablename)
        _init = partial(t.from_dict, plain=True) if as_dict else t.from_iterable
        self.add_rows(tablename,
            [_init(d) for d in rows],
            verbose=verbose)
    
    def load(self, data, tables=None, exclude_tables=None, as_dict=False, clear=True, verbose=True):
        tables = self._get_included_tables(tables, exclude_tables)
        if clear:
            for tablename in (tables or data.iterkeys()):
                self.clear_table(tablename, commit=False)
                self.create_table(tablename, commit=False)
            self.commit()
        for tablename in (tables or data.iterkeys()):
            rows = data.get(tablename)
            if rows:
                self.load_table(tablename, rows, as_dict=as_dict, clear=False, verbose=verbose)


DB_SQLITE3 = 1


def get_db_interface_class(dbname, dbtype, structure, params):
    if dbtype is DB_SQLITE3:
        from plib.stdlib.dbtools.sqlite import SQLite3DBInterface
        intf_class = SQLite3DBInterface
    # TODO: add MySQL support
    else:
        raise RuntimeError("Invalid database type: {0}".format(repr(dbtype)))
    
    if isinstance(structure, str):
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
    # TODO: kwds not used until MySQL support is added
    else:
        raise RuntimeError("Invalid database type: {0}".format(repr(dbtype)))
    return args, kwargs


def get_db_interface(dbname, dbtype, structure, params, argpath, kwds):
    klass = get_db_interface_class(dbname, dbtype, structure, params)
    args, kwargs = get_db_interface_args(dbname, dbtype, argpath, kwds)
    return klass(*args, **kwargs)
