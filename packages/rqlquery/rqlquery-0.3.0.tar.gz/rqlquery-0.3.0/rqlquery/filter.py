"""Build a where clause from a json filter

The filter is composed by nested dictionnaries and lists of attribute names,
values and operators.

Below is a clumsy formalisation of the filter format:

FILTER
    CRITERION_LIST    -> equivalent to {"$and": CRITERION_LIST}
    COMBINATION_OPERATION
    UNARY_OPERATION

COMBINATION_OPERATION
    {"$or": CRITERION_LIST}
    {"$and": CRITERION_LIST}

UNARY_OPERATION
    {"$not": FILTER}

CRITERION_LIST
    [FILTER, ...]
    Dictionnary of CRITERION

CRITERION
    "attrname": OPERATION_LIST
    "relation": FILTER

    "relation": OPERATION_LIST
        -> equivalent to "relation": {"eid": OPERATION_LIST}

    "relation": true
        -> True if such a relation to an existing entity exists.

OPERATION_LIST
    VALUE   -> equivalent to {"$eq": VALUE}
    Dictionnary of OPERATION

OPERATION
    "$op": VALUE

VALUE
    A literal value, or a list of literal values

"""

from __future__ import absolute_import

import datetime
import iso8601

from . import query

SameTypeArg = object()


query_operators = {
    '$eq': query.Equal,
    '$ne': query.NotEqual,
    '$gt': query.Greater,
    '$ge': query.GreaterOrEqual,
    '$lt': query.Less,
    '$le': query.LessOrEqual,
    '$in': query.In,
    '$nin': query.NotIn,
    '$like': query.Like,
    '$ilike': query.ILike,
}

query_combination_operators = {
    '$and': query.And,
    '$or': query.Or
}

query_unary_operators = {
    '$not': query.Not
}


def read_date(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value
    return iso8601.parse_date(value).date()


def read_time(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value
    return datetime.datetime.strptime(value, '%H:%M:%S').time()


def read_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')


def read_tzdatetime(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value
    return iso8601.parse_date(value)


class FilterParser(object):
    value_parser = {
        'Date': read_date,
        'Time': read_time,
        'Datetime': read_datetime,
        'TZDatetime': read_tzdatetime
    }

    def __init__(self, schema, etype=None, data=None):
        self.schema = schema
        self.etype = etype
        self.data = data

    def is_operation_list(self, data):
        if isinstance(data, dict):
            return iter(data).next() in query_operators
        return data is not True and not isinstance(data, list)

    def is_unary_operation(self, data):
        return (
            isinstance(data, dict)
            and len(data) == 1
            and iter(data).next() in query_unary_operators)

    def is_filter(self, data):
        return (
            isinstance(data, dict)
            and len(data) == 1
            and list(data.keys())[0] in ('$or', '$and'))

    def parse(self, etype=None, data=None):
        return self.parse_filter(
            self.schema.eschema(etype or self.etype), data or self.data)

    def parse_filter(self, eschema, data):
        # FILTER
        if self.is_unary_operation(data):
            op, subfilter = iter(data.items()).next()
            return query_unary_operators[op](
                self.parse_filter(eschema, subfilter))
        if self.is_filter(data):
        #     {"$or": CRITERION_LIST}
        #     {"$and": CRITERION_LIST}
            key, criterion_list_data = iter(data.items()).next()
            operator = query_combination_operators[key]
        else:
        #     CRITERION_LIST    -> equivalent to {"$and": CRITERION_LIST}
            operator = query.And
            criterion_list_data = data

        criterion_list = self.parse_criterion_list(
            eschema, criterion_list_data)

        if len(criterion_list) == 1:
            return criterion_list[0]

        return operator(*criterion_list)

    def parse_rtype(self, rtype):
        if '[' in rtype:
            etype_hint = rtype[rtype.index('[')+1:-1]
            rtype = rtype[:rtype.index('[')]
        else:
            etype_hint = None
        if rtype[0] == '<':
            rtype, role = rtype[1:], 'object'
        else:
            role = 'subject'
        rschema = self.schema.rschema(rtype)
        if rschema.final and role != 'subject':
            raise ValueError("Cannot reverse an attribute")
        return rschema, role, etype_hint

    def parse_rtypes(self, rtypes):
        return [
            self.parse_rtype(rtype)
            for rtype in rtypes.split('.')
        ]

    def parse_criterion_list(self, eschema, data):
        # CRITERION_LIST
        #     [FILTER, ...]
        if isinstance(data, list):
            return [
                self.parse_filter(eschema, item)
                for item in data]
        #     Dictionnary of CRITERION
        elif isinstance(data, dict):
            return [
                self.parse_criterion(eschema, rtype, criterion)
                for rtype, criterion in data.items()]
        raise ValueError(
            "Expected a list or a dict as criterion_list, got %s" % data)

    def parse_criterion(self, eschema, rtypes, data):
        relations = self.parse_rtypes(rtypes)

        path = []

        for rschema, role, etype_hint in relations:
            if rschema.final:
                break
            path.append((rschema, role))
            targets = rschema.targets(eschema.type, role)

            if not etype_hint and len(targets) > 1:
                raise ValueError(
                    "Polymorphic relation %s is missing an etype hint" %
                    rschema.type)
            if not etype_hint:
                eschema = targets[0]
            else:
                eschema = next(x for x in targets if x.type == etype_hint)

        if len(relations) - len(path) > 1:
            raise ValueError(rtypes + " has a final relation in the path")

        # CRITERION
        #     "attrname": OPERATION_LIST
        if rschema.final:
            condition = self.parse_operation_list(
                eschema, rschema, data)

        else:
            if self.is_operation_list(data):
        #     "relation": OPERATION_LIST
        #         -> equivalent to "relation": {"eid": OPERATION_LIST}
                filter = {'eid': data}
            else:
                filter = data
        #     "relation": true
            if filter is True:
                condition = True
            else:
        #     "relation": FILTER
                condition = self.parse_filter(eschema, filter)

        if path:
            for rschema, role in reversed(path):
                condition = query.SubFilter(rschema.type, role, condition)
            condition = query.Exists(condition)

        return condition

    def parse_operation_list(self, eschema, rschema, data):
        # OPERATION_LIST

        #     VALUE   -> equivalent to {"$eq": VALUE}
        if not isinstance(data, dict):
            conditions = [self.parse_operation(eschema, rschema, '$eq', data)]

        #     Dictionnary of OPERATION
        else:
            conditions = [
                self.parse_operation(eschema, rschema, op, value)
                for op, value in data.items()]
        if len(conditions) == 1:
            return conditions[0]
        return query.And(*conditions)

    def parse_operation(self, eschema, rschema, op, value):
        # OPERATION
        #     "$op": VALUE
        #     "$op": {'key': VALUE, 'key': value}
        assert rschema.final
        op = query_operators[op]
        if isinstance(op, tuple):
            op, argtypes = op
            args = {}
            for key, type in argtypes.items():
                argvalue = value[key]
                if type is SameTypeArg:
                    type = rschema.targets(eschema.type)[0]
                else:
                    type = self.schema.eschema(type)
                args[key] = self.parse_value(type, argvalue)
        else:
            args = {
                'value': self.parse_value(
                    rschema.targets(eschema.type)[0], value)}
        return op(rschema.type, **args)

    def parse_value(self, eschema, data):
        # VALUE
        #     A literal value, or a list of literal values
        # XXX Take the eschema in consideration to convert the value to the
        # right data type
        assert eschema.final
        if eschema.type in self.value_parser:
            return self.value_parser[eschema.type](data)
        return data
