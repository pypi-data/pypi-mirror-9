#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Joachim Jablon

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Python Future imports
from __future__ import unicode_literals

# Python System imports
import csv
import sys
import argparse

# Third-party imports
import six

# Relative imports


class ExcelWithSemicolon(csv.excel):
    if six.PY2:
        delimiter = b";"
    else:
        delimiter = ";"


class AgnosticReader(object):
    """
    A csv reader that can read both CSV and VSPDPV ("Valeurs Separees Par
    Des Points-Virgules", a.k.a CSV files formated by Excel with regionalization
    parameters set to a place where the decimal mark is a comma, and the csv
    separator a semicolon.)
    The whole point is that the lack of standardization of the CSV format
    makes it hard to parse when the precise regionalization parameters are not known.
    We are deeply sorry for the writers of RFC 4180.

    Class is not a CSV Reader subclass because, in python 2.7, csv.DictReader
    is an old-style class, which makes inheritance complicated.
    """
    Error = csv.Error
    digits = set("{}".format(val) for val in range(10))
    comma_set = set(",")

    def __init__(self, csvfile, *args, **kwargs):
        if "dialect" not in kwargs:
            dialect = csv.excel

            csvfile = six.StringIO(csvfile.read())

            beginning = csvfile.read(1024)
            csvfile.seek(0)

            if beginning.count(";") > beginning.count(","):
                dialect = ExcelWithSemicolon

            kwargs.update({"dialect": dialect})

        self.dict_reader = csv.DictReader(csvfile, *args, **kwargs)

    @classmethod
    def replace_decimal(cls, value):
        if value is not None and set(value) - cls.digits == cls.comma_set:
            return value.replace(",", ".")
        return value

    def __iter__(self):
        for element_dict in self.dict_reader:
            yield {key: self.replace_decimal(value) for key, value in six.iteritems(element_dict)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType("r"), default=sys.stdin)
    parser.add_argument('output_file', type=argparse.FileType("w"), default=sys.stdout)
    args = parser.parse_args()

    reader = AgnosticReader(args.input_file)
    writer = csv.DictWriter(args.output_file, fieldnames=reader.dict_reader.fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(reader)

if __name__ == '__main__':
    main()
