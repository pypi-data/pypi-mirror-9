"""
Experimental Query object inspired by SQLAlchemy Query object.

See test/test_query.py for example of how to use it.
"""

from rql.utils import rqlvar_maker

import cubicweb.req


def _generative(fn):
    def newfunc(self, *args, **kwargs):
        self = self._clone()
        fn(self, *args, **kwargs)
        return self
    return newfunc


class OrderBy(object):
    # XXX instead of just 'rtype', we should be able to pass an expression.
    # For e.g. : OrderBy(LENGTH(rtype))
    def __init__(self, rtype, direction='ASC'):
        self.direction = direction
        self.rtype = rtype

    def torql(self, evarname, varmaker, params):
        varname = varmaker.next()
        return (
            "%s %s" % (varname, self.direction),
            "%s %s %s" % (evarname, self.rtype, varname))


class ParamsHolder(dict):
    def __init__(self):
        super(ParamsHolder, self).__init__()
        self.varmaker = rqlvar_maker()

    def newparam(self, value):
        name = self.varmaker.next()
        self[name] = value
        return name


class Condition(object):
    priority = None

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)


class FinalCondition(Condition):
    priority = 0

    def __init__(self, rtype, value):
        self.rtype = rtype
        self.value = value

    def make_condition(self, params):
        return "%s %%(%s)s" % (self.operator, params.newparam(self.value))

    def torql(self, evarname, varmaker, params):
        condition = self.make_condition(params)
        return "%s %s %s" % (evarname, self.rtype, condition)


class Equal(FinalCondition):
    operator = '='


class NotEqual(FinalCondition):
    operator = '!='


class Greater(FinalCondition):
    operator = '>'


class GreaterOrEqual(FinalCondition):
    operator = '>='


class Less(FinalCondition):
    operator = '<'


class LessOrEqual(FinalCondition):
    operator = '<='


class Like(FinalCondition):
    operator = "LIKE"


class ILike(FinalCondition):
    operator = "ILIKE"


class Is(FinalCondition):
    operator = 'is'

    def __init__(self, etype):
        self.etype = etype

    def torql(self, evarname, varmaker, params):
        return "%s is %s" % (evarname, self.etype)


class ListFinalCondition(FinalCondition):
    def __init__(self, rtype, value):
        super(ListFinalCondition, self).__init__(rtype, value)

    def make_condition(self, params):
        return "%s (%s)" % (
            self.operator,
            ', '.join('%%(%s)s' % params.newparam(v) for v in self.value))


class In(ListFinalCondition):
    operator = 'IN'


def NotIn(rtype, value):
    return Not(In(rtype, value))


class Not(Condition):
    priority = 5

    def __init__(self, condition):
        self.condition = condition

    def torql(self, evarname, varmaker, params):
        rql = self.condition.torql(evarname, varmaker, params)
        if 'where' in rql:
            where = rql['where']
        else:
            where = rql
            rql = {}

        if self.condition.priority > self.priority:
            where = "(%s)" % where

        rql['where'] = "NOT %s" % where

        return rql


class BooleanOperation(Condition):
    def __init__(self, *conditions):
        self.conditions = conditions
        self._op = " %s " % self.operator

    def torql(self, evarname, varmaker, params):
        where = []
        having = []
        for c, rql in (
                (c, c.torql(evarname, varmaker, params))
                for c in self.conditions):
            need_parenthesis = c.priority > self.priority
            if isinstance(rql, dict):
                where.append(rql['where'])
                if 'having' in rql:
                    having.append(rql['having'])
            else:
                where.append(rql)
            if need_parenthesis:
                where[-1] = "(%s)" % where[-1]
        r = {'where': self._op.join(where)}
        if having:
            r['having'] = ', '.join(having)
        return r


class And(BooleanOperation):
    operator = "AND"

    priority = 6

    def __and__(self, other):
        if isinstance(other, And):
            return And(*(self.conditions + other.conditions))
        return And(*(self.conditions + (other,)))

    def __rand__(self, other):
        if isinstance(other, And):
            return And(*(self.conditions + other.conditions))
        return And(*(self.conditions + (other,)))


class Or(BooleanOperation):
    operator = "OR"

    priority = 7

    def __or__(self, other):
        if isinstance(other, Or):
            return Or(*(self.conditions + other.conditions))
        return Or(*(self.conditions + (other,)))

    def __ror__(self, other):
        return self.__or__(other)


class SubFilter(object):
    priority = 8

    def __init__(self, rtype, role, *conditions, **kwconds):
        self.rtype = rtype
        self.role = role
        self.conditions = list(conditions)
        self.conditions.extend(
            Equal(rtype, value)
            for rtype, value in kwconds.items())

    def torql(self, evarname, varmaker, params):
        tgt_evarname = varmaker.next()
        if self.role == 'subject':
            svar, ovar = evarname, tgt_evarname
        elif self.role == 'object':
            svar, ovar = tgt_evarname, evarname
        where = []
        having = []

        if len(self.conditions) == 1 and self.conditions[0] is True:
            rql = {'where': "%s %s %s" % (
                svar, self.rtype, ovar)}
        else:
            for rql in (
                    c.torql(tgt_evarname, varmaker, params)
                    for c in self.conditions):

                if isinstance(rql, basestring):
                    where.append(rql)
                else:
                    where.append(rql['where'])
                    if 'having' in rql:
                        having.append(rql['having'])

            rql = {'where': "%s %s %s, %s" % (
                svar, self.rtype, ovar, ", ".join(where))}
            if having:
                rql['having'] = ", ".join(having)

        return rql


class Exists(Condition):
    priority = 0

    def __init__(self, condition):
        self.condition = condition

    def torql(self, evarname, varmaker, params):
        r = self.condition.torql(evarname, varmaker, params)
        if isinstance(r, dict):
            r['where'] = "EXISTS (%s)" % r['where']
        else:
            r = "EXISTS (%s)" % r
        return r


class RelationOps(object):
    def __init__(self, rtype, role='subject'):
        self.rtype = rtype
        self.role = role

    def exists(self, *conds, **kwconds):
        if not conds and not kwconds:
            conds = [True]
        return Exists(self.filter(*conds, **kwconds))

    def filter(self, *conds, **kwconds):
        return SubFilter(self.rtype, self.role, *conds, **kwconds)


class AttributeOps(object):
    def __init__(self, rtype):
        self.rtype = rtype

    def __eq__(self, value):
        return Equal(self.rtype, value)

    def __ne__(self, value):
        return NotEqual(self.rtype, value)

    def __gt__(self, value):
        return Greater(self.rtype, value)

    def __ge__(self, value):
        return GreaterOrEqual(self.rtype, value)

    def __lt__(self, value):
        return Less(self.rtype, value)

    def __le__(self, value):
        return LessOrEqual(self.rtype, value)

    def in_(self, values):
        return In(self.rtype, values)

    def notin(self, values):
        return NotIn(self.rtype, values)

    def like(self, value):
        return Like(self.rtype, value)

    def ilike(self, value):
        return ILike(self.rtype, value)

from cubicweb.entity import Relation, Attribute


def Relation__get__(self, eobj, eclass):
    if eobj is None:
        return RelationOps(self._rtype, self._role)
    return eobj.related(self._rtype, self._role, entities=True)

Relation.__get__ = Relation__get__


def Attribute__get__(self, eobj, eclass):
    if eobj is None:
        return AttributeOps(self._attrname)
    return eobj.cw_attr_value(self._attrname)


Attribute.__get__ = Attribute__get__


class Query(object):
    def __init__(self, schema, etype, cnx=None):
        self.schema = schema
        self.cnx = cnx
        if not isinstance(etype, basestring):
            etype = etype.cw_etype
        self.etype = etype
        self.eschema = self.schema.eschema(etype)
        self._columns = []
        self.varmaker = rqlvar_maker(defined=['X'])
        self.select = []
        self.conditions = [Is(self.etype)]
        self._limit = None
        self._offset = None
        self._orderby = []

    def _clone(self):
        q = Query(self.schema, self.etype, self.cnx)
        q._columns = list(self._columns)
        q.varmaker = rqlvar_maker(
            stop=self.varmaker.stop,
            index=self.varmaker.index,
            defined=self.varmaker.defined,
            aliases=self.varmaker.aliases)
        q.select = list(self.select)
        q.conditions = list(self.conditions)
        q._limit = self._limit
        q._offset = self._offset
        q._orderby = list(self._orderby)
        return q

    @_generative
    def add_column(self, *rtypes):
        self._columns.extend(
            rtype.split('.') if isinstance(rtype, basestring) else rtype
            for rtype in rtypes)
        return self

    @_generative
    def filter(self, *conds, **kwconds):
        for rtype, value in kwconds.items():
            self.conditions.append(Equal(rtype, value))
        self.conditions.extend(conds)
        return self

    @_generative
    def limit(self, limit):
        self._limit = limit
        return self

    @_generative
    def offset(self, offset):
        self._offset = offset
        return self

    @_generative
    def orderby(self, *orderby_list):
        for orderby in orderby_list:
            if not isinstance(orderby, OrderBy):
                if orderby.startswith('-'):
                    rtype, direction = orderby[1:], 'DESC'
                elif ' ' in orderby:
                        rtype, direction = orderby.split(' ')
                        direction = direction.upper()
                else:
                    rtype, direction = orderby, 'ASC'
                self._orderby.append(OrderBy(rtype, direction))
            else:
                self._orderby.append(orderby)
        return self

    def torql(self):
        params = ParamsHolder()
        varmaker = rqlvar_maker()
        clauses = []
        having = []
        select = ["X"]

        for condition in self.conditions:
            rql = condition.torql("X", varmaker, params)
            if not isinstance(rql, dict):
                where = rql
            else:
                where = rql['where']

                if 'having' in rql:
                    having.append(rql['having'])

            clauses.append(where)

        for path in self._columns:
            var = 'X'
            for i, rtype in enumerate(path):
                varname = "{}_{}".format(var, rtype.upper())
                clause = "{} {} {}".format(var, rtype, varname)
                rschema = self.schema.rschema(rtype)
                if not rschema.final:
                    for rdef in rschema.rdefs.values():
                        if rdef.cardinality[0] not in '1+':
                            clause += '?'
                            break

                # Add the varname to the selection list if corresponds to the
                # final segment of the path.
                # For example, a column 'in_group.name' would select
                # X_IN_GROUP_NAME, but not X_IN_GROUP
                if i + 1 == len(path) and varname not in select:
                    select.append(varname)

                # Add the clause in the list if not yet present.
                # This simple trick will avoid multiple clause reaching the
                # same relation since the varnames are predictible.
                if clause not in clauses:
                    clauses.append(clause)
                var = varname

        # XXX We should be able to match the attributes already in _columns
        # and use them directly if needed.
        orderby_list = []
        for orderby in self._orderby:
            orderby_clause, where_clause = orderby.torql("X", varmaker, params)
            orderby_list.append(orderby_clause)
            clauses.append(where_clause)

        rql = "Any " + ', '.join(select)

        if orderby_list:
            rql += " ORDERBY " + ', '.join(orderby_list)
        if self._limit:
            rql += " LIMIT " + str(self._limit)
        if self._offset:
            rql += " OFFSET " + str(self._offset)
        if clauses:
            rql += " WHERE " + ', '.join(clauses)
        if having:
            rql += " HAVING " + ', '.join(having)

        return rql, params

    def execute(self, cnx=None):
        cnx = cnx or self.cnx
        return cnx.execute(*self.torql())

    def all(self, cnx=None):
        return self.execute(cnx).entities()

    def one(self, cnx=None):
        return self.limit(2).execute(cnx).one()

    def exists(self, cnx=None):
        rset = self.limit(1).execute(cnx)
        return rset.rowcount == 1

    def __iter__(self):
        return self.all()


def request_query(self, etype):
    return Query(self.vreg.schema, etype, cnx=self.cnx)

cubicweb.req.RequestSessionBase.query = request_query
