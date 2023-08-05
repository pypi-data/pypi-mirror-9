#!/usr/bin/env python
"""
Module CSVTOOLS -- PLIB CSV File Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2014 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities that build on the
standard library ``csv`` module.
"""

import csv
from codecs import getreader, BOM_UTF8, BOM_UTF16, BOM_UTF16_BE, BOM_UTF16_LE
from contextlib import closing
from cStringIO import StringIO


class UTF8Recoder:
    """Iterator that reads an encoded stream and reencodes the input to UTF-8.
    
    (From Python 2.7 CSV module documentation.)
    """
    def __init__(self, f, encoding):
        self.reader = getreader(encoding)(f)
    
    def __iter__(self):
        return self
    
    def next(self):
        return self.reader.next().encode("utf-8")


def _csv_row(rd):
    # CSV functions can only handle utf-8 bytes, not unicode
    return [unicode(f, "utf-8") for f in next(rd)]


def _csv_iter(f, encoding, has_header):
    rd = iter(csv.reader(UTF8Recoder(f, encoding)))
    hdr = _csv_row(rd) if has_header else []
    return hdr, (_csv_row(r) for r in rd)


def rows_from_csv(filename, encoding='utf-8', has_header=True, return_header=False):
    with open(filename, 'rb') as f:
        hdr, rd = _csv_iter(f, encoding, has_header)
        rows = list(rd)
        return hdr, rows if has_header and return_header else rows


def dict_from_csv(filename, encoding='utf-8', multi=False, has_header=True, return_header=False):
    # Assumes each row in CSV has only two fields unless multi is True
    with open(filename, 'rb') as f:
        hdr, rd = _csv_iter(f, has_header)
        if multi:
            result = dict((row[0], row[1:]) for row in rd)
        else:
            result = dict(rd)
        return hdr, result if has_header and return_header else result


BOM_MAP = {
    'utf-8': BOM_UTF8,
    'utf-16': BOM_UTF16,
    'utf-16-be': BOM_UTF16_BE,
    'utf-16-le': BOM_UTF16_LE
}


def write_csv(rows, filename, encoding='utf-8', write_bom=False, write_bom_by_char=False,
              bom_map=BOM_MAP, replacements=None):
    
    # Easier than writing a context manager wrapper for cStringIO
    f = StringIO()
    try:
        wr = csv.writer(f)
        for row in rows:
            # CSV functions can only handle utf-8 encoded bytes, not unicode
            wr.writerow([u.encode('utf-8') for u in row])
        s = f.getvalue()
    finally:
        f.close()
    # Decode/encode to get output into desired encoding
    b = s.decode('utf-8').encode(encoding)
    
    bom = bom_map.get(encoding)
    if bom:
        if write_bom:
            b = bom + b
        if write_bom_by_char and replacements:
            for rb in replacements[encoding]:
                b = b.replace(rb, bom + rb)
    
    with open(filename, 'wb') as f:
        f.write(b)
