# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
from . import base


RESULTS = {
    'empty_header': {
        'id': 'empty_header',
        'name': 'Empty Header',
        'msg': 'The header in column {0} was found to be empty.',
        'help': '',
        'help_edit': ''
    },
    'duplicate_header': {
        'id': 'duplicate_header',
        'name': 'Duplicate Header',
        'msg': 'The header in column {0} was found to have duplicates.',
        'help': '',
        'help_edit': ''
    },
    'defective_row': {
        'id': 'defective_row',
        'name': 'Defective Row',
        'msg': 'Row {0} is defective: the dimensions are incorrect compared to headers.',
        'help': '',
        'help_edit': ''
    },
    'duplicate_row': {
        'id': 'duplicate_row',
        'name': 'Duplicate Row',
        'msg': 'Row {0} duplicates the following rows which have already been seen: {1}.',
        'help': '',
        'help_edit': ''
    },
    'empty_row': {
        'id': 'empty_row',
        'name': 'Empty Row',
        'msg': 'Row {0} is empty.',
        'help': '',
        'help_edit': ''
    }
}


class StructureProcessor(base.Processor):

    name = 'structure'
    RESULT_TYPES = RESULTS

    def __init__(self, fail_fast=False, transform=False, report_limit=1000,
                 row_limit=30000, ignore_empty_rows=False,
                 ignore_duplicate_rows=False, ignore_defective_rows=False,
                 ignore_empty_columns=False, ignore_duplicate_columns=False,
                 ignore_headerless_columns=False, empty_strings=None,
                 report_stream=None, report=None, result_level='error',
                 **kwargs):

        # TODO: `self.seen` should be maintained in a file or something
        # TODO: Check for empty columns

        super(StructureProcessor, self).__init__(
            fail_fast=fail_fast, transform=transform, report_limit=report_limit,
            row_limit=row_limit, report_stream=report_stream, report=report,
            result_level=result_level)

        self.ignore_empty_rows = ignore_empty_rows
        self.ignore_duplicate_rows = ignore_duplicate_rows
        self.ignore_defective_rows = ignore_defective_rows
        self.ignore_empty_columns = ignore_empty_columns
        self.ignore_duplicate_columns = ignore_duplicate_columns
        self.ignore_headerless_columns = ignore_headerless_columns
        self.empty_strings = empty_strings or ('',)
        self.seen = {}

    def run_header(self, headers, header_index=0):

        valid = True

        # check for headerless columns
        if not self.ignore_headerless_columns:
            for index, header in enumerate(headers):
                if header in self.empty_strings:

                    valid = False
                    _type = RESULTS['empty_header']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(index),
                        _type['id'],
                        _type['name'],
                        headers,
                        header_index,
                        self.RESULT_HEADER_ROW_NAME,
                        index,
                        header
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers

        # check for duplicate columns
        if not self.ignore_duplicate_columns:
            if len(set(headers)) != len(headers):

                valid = False
                dupes = [(index, header) for index, header in
                         enumerate(headers) if
                         header.count(header) > 1]
                _type = RESULTS['duplicate_header']

                for dupe in dupes:
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(dupe[0]),
                        _type['id'],
                        _type['name'],
                        headers,
                        header_index,
                        self.RESULT_HEADER_ROW_NAME,
                        dupe[0],
                        dupe[1]
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers

        return valid, headers

    def run_row(self, headers, index, row):

        valid, is_dupe, is_empty, is_defective = True, False, False, False
        row_name = self.get_row_id(row, headers)

        # check if row is duplicate
        if not self.ignore_duplicate_rows:

            _rep = hash(frozenset(row))

            if _rep in self.seen:

                # don't keep writing results for totally empty rows
                if set(row) == set(['']):
                    pass
                else:
                    previous_instances = copy.deepcopy(self.seen[_rep])
                    self.seen[_rep].append(index)
                    valid = False
                    is_dupe = True
                    _type = RESULTS['duplicate_row']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_ROW,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(index, previous_instances),
                        _type['id'],
                        _type['name'],
                        row,
                        index,
                        row_name
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers, index, row

            else:
                self.seen[_rep] = [index]

        # check if row is empty
        if not self.ignore_empty_rows:
            as_set = set(row)
            if len(as_set) == 1 and \
                    set(self.empty_strings).intersection(as_set):

                valid = False
                is_empty = True
                _type = RESULTS['empty_row']
                entry = self.make_entry(
                    self.name,
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _type['msg'].format(index),
                    _type['id'],
                    _type['name'],
                    row,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

        # check if row is defective
        if not self.ignore_defective_rows:
            if len(headers) < len(row):

                valid = False
                is_defective = True
                _type = RESULTS['defective_row']
                entry = self.make_entry(
                    self.name,
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _type['msg'].format(index),
                    _type['id'],
                    _type['name'],
                    row,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

            elif len(headers) < len(row):

                valid = False
                is_defective = True
                _type = RESULTS['defective_row']
                entry = self.make_entry(
                    self.name,
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _type['msg'].format(index),
                    _type['id'],
                    _type['name'],
                    row,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

        if self.transform and any([is_dupe, is_empty, is_defective]):
            row = None

        return valid, headers, index, row
