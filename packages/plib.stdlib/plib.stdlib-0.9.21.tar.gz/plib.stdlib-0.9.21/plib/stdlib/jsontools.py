#!/usr/bin/env python
"""
Module JSONTOOLS -- Tools for JSON and similar file formats
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2014 by Peter A. Donis

These are convenience functions for loading/saving JSON
from/to filenames. Also, functions are added to support
"extended" JSON, which includes tuples and other non-dynamic
Python types that standard JSON does not support. Note that
no checking is done in the "extended" methods to ensure that
only "allowed" types are used when saving/dumping; the only
check is done on loading, since ``ast.literal_eval`` will
only accept certain types.
"""

from ast import literal_eval
from codecs import encode, decode
from json import load, dump


def load_json(filename, encoding='utf-8', universal_newlines=True):
    with open(filename, 'r{}'.format('U' if universal_newlines else '')) as f:
        return load(f, encoding=encoding)


def save_json(data, filename, encoding='utf-8'):
    with open(filename, 'w') as f:
        dump(data, f, encoding=encoding)


def loads_ext(s, encoding='utf-8'):
    return literal_eval(decode(s, encoding))


def load_ext(f, encoding='utf-8'):
    return loads_ext(f.read(), encoding=encoding)


def dumps_ext(obj, encoding='utf-8'):
    return encode(repr(obj), encoding)


def dump_ext(data, f, encoding='utf-8'):
    f.write(dumps_ext(data, encoding=encoding))


def load_json_ext(filename, encoding='utf-8', universal_newlines=True):
    with open(filename, 'r{}'.format('U' if universal_newlines else '')) as f:
        return load_ext(f, encoding=encoding)


def save_json_ext(data, filename, encoding='utf-8'):
    with open(filename, 'w') as f:
        dump_ext(data, f, encoding=encoding)
