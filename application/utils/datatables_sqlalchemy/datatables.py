# -*- coding: utf-8 -*-
import sys
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.sql import or_, and_
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import cast
from sqlalchemy import String
from collections import namedtuple
from logging import getLogger
from copy import deepcopy


log = getLogger(__file__)
row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
if sys.version_info > (3, 0):
    unicode = str
ColumnTuple = namedtuple(
    'ColumnDT',
    ['column_name', 'mData', 'search_like', 'filter', 'searchable'])


def get_attr(sqla_object, attribute):
    output = sqla_object
    for x in attribute.split('.'):
        if type(output) is InstrumentedList:
            output = ', '.join([getattr(elem, x) for elem in output])
        else:
            output = getattr(output, x)
    return output


class ColumnDT(ColumnTuple):
    def __new__(cls, column_name, mData=None, search_like=None,
                filter=str, searchable=True):
        return super(ColumnDT, cls).__new__(cls, column_name, mData, search_like, filter, searchable)


class DataTables:
    def __init__(self, request, sqla_object, query, columns):
        self.request_values = deepcopy(dict(request.args))
        for key in self.request_values:
            self.request_values[key] = self.request_values[key][0]
        for key, value in self.request_values.items():
            try:
                self.request_values[key] = int(value)
            except ValueError:
                if value in ("true", "false"):
                    self.request_values[key] = value == "true"
        self.sqla_object = sqla_object
        self.query = query
        self.columns = columns
        self.results = None
        self.cardinality_filtered = 0
        self.cardinality = 0
        self.run()


    def output_result(self):
        output = {}
        output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality_filtered)
        output['aaData'] = self.results
        return output


    def run(self):
        self.cardinality = self.query.count()
        rez = []
        for row in self.query.all():
            rez.append(row)
        self.filtering()
        self.sorting()
        self.paging()
        rez = []
        for row in self.query.all():
            rez.append(row2dict(row))
        self.results = rez
        formatted_results = []
        for i in range(len(rez)):
            row = dict()
            for j in range(len(self.columns)):
                col = self.columns[j]
                tmp_row = self.results[i][col.column_name]
                if col.filter:
                    if sys.version_info < (3, 0) \
                            and hasattr(tmp_row, 'encode'):
                        tmp_row = col.filter(tmp_row.encode('utf-8'))
                    tmp_row = col.filter(tmp_row)
                row[col.mData if col.mData else str(j)] = tmp_row
            formatted_results.append(row)
        self.results = formatted_results


    def filtering(self):
        search_value = self.request_values.get('sSearch')
        condition = None


        def search(idx, col):
            tmp_column_name = col.column_name.split('.')
            for tmp_name in tmp_column_name:
                if tmp_column_name.index(tmp_name) == 0:
                    obj = getattr(self.sqla_object, tmp_name)
                    parent = self.sqla_object
                elif isinstance(obj.property, RelationshipProperty):
                    parent = obj.property.mapper.class_
                    obj = getattr(parent, tmp_name)
                if not hasattr(obj, 'property'):
                    sqla_obj = parent
                    column_name = tmp_name
                elif isinstance(obj.property, RelationshipProperty):
                    sqla_obj = obj.mapper.class_
                    column_name = tmp_name
                    if not column_name:
                        column_name = obj.property.table.primary_key.columns \
                            .values()[0].name
                else:
                    sqla_obj = parent
                    column_name = tmp_name
            return sqla_obj, column_name
        if search_value:
            search_value_list = str(search_value).split()
            for search_val in search_value_list:
                conditions = []
                for idx, col in enumerate(self.columns):
                    if self.request_values.get('bSearchable_%s' % idx) in (
                            True, 'true') and col.searchable:
                        sqla_obj, column_name = search(idx, col)
                        conditions.append(
                            cast(get_attr(sqla_obj, column_name), String).ilike('%%%s%%' % search_val))
                condition = or_(*conditions)
                if condition is not None:
                    self.query = self.query.filter(condition)
        conditions = []
        for idx, col in enumerate(self.columns):
            search_value2 = self.request_values.get('sSearch_%s' % idx)
            if search_value2:
                sqla_obj, column_name = search(idx, col)
                if col.search_like:
                    conditions.append(
                        cast(get_attr(sqla_obj, column_name), String).ilike('%%%s%%' % search_value2))
                else:
                    conditions.append(
                        cast(get_attr(sqla_obj, column_name), String).__eq__(search_value2))
                if condition is not None:
                    condition = and_(condition, and_(*conditions))
                else:
                    condition = and_(*conditions)
        if condition is not None:
            self.query = self.query.filter(condition)
            self.cardinality_filtered = self.query.count()
        else:
            self.cardinality_filtered = self.cardinality


    def sorting(self):
        sorting = []
        Order = namedtuple('order', ['name', 'dir'])
        if self.request_values.get('iSortingCols') > 0:
            for i in range(int(self.request_values['iSortingCols'])):
                sorting.append(Order(self.columns[int(self.request_values['iSortCol_' + str(i)])].column_name, self.request_values['sSortDir_' + str(i)]))
        for sort in sorting:
            tmp_sort_name = sort.name.split('.')
            for tmp_name in tmp_sort_name:
                if tmp_sort_name.index(tmp_name) == 0:
                    obj = getattr(self.sqla_object, tmp_name)
                    parent = self.sqla_object
                elif isinstance(obj.property, RelationshipProperty):
                    parent = obj.property.mapper.class_
                    obj = getattr(parent, tmp_name)
                if not hasattr(obj, "property"):
                    sort_name = tmp_name
                    if hasattr(parent, "__tablename__"):
                        tablename = parent.__tablename__
                    else:
                        tablename = parent.__table__.name
                elif isinstance(obj.property, RelationshipProperty):
                    sort_name = tmp_name
                    if not sort_name:
                        sort_name = obj.property.table.primary_key.columns \
                            .values()[0].name
                    tablename = obj.property.table.name
                else:
                    sort_name = tmp_name
                    if hasattr(parent, "__tablename__"):
                        tablename = parent.__tablename__
                    else:
                        tablename = parent.__table__.name

            sort_name = "%s.%s" % (tablename, sort_name)
            self.query = self.query.order_by(
                asc(sort_name) if sort.dir == 'asc' else desc(sort_name))


    def paging(self):
        pages = namedtuple('pages', ['start', 'length'])
        if (self.request_values['iDisplayStart'] != "") \
                and (self.request_values['iDisplayLength'] != -1):
            pages.start = int(self.request_values['iDisplayStart'])
            pages.length = int(self.request_values['iDisplayLength'])
        offset = pages.start + pages.length
        self.query = self.query.slice(pages.start, offset)