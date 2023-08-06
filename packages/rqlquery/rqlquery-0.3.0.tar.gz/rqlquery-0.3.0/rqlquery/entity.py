import itertools
from collections import defaultdict

from rql.stmts import Select
from rql.nodes import (
    Function, VariableRef, make_relation, make_constant_restriction)

from cubicweb.rset import ResultSet


def fill_relation_cache(
        cnx, entities, rtype, role, fetchattrs=None, force=False):
    """
    Read a relation several entities at once and fill their relation_cache.
    Entities that already have the cache filled will be ignored unless `force`
    is `True`.
    """
    entities = list(entities)

    rqlst = fetch_relation_rqlst(cnx, entities, rtype, role, fetchattrs, force)
    if rqlst is None:
        return
    rql = rqlst.as_string()

    target_entities = defaultdict(list)

    rset = cnx.execute(rql)
    for i, row in enumerate(rset):
        sources = [int(eid) for eid in row[0].split(',')]
        tgt_entity = rset.get_entity(i, 1)
        for source in sources:
            target_entities[source].append(tgt_entity)

    for entity in entities:
        rql = None  # XXX forge a rql request that returns the entities.
        related = target_entities[entity.eid]
        rset = ResultSet(
            [[e.eid] for e in related], rql,
            description=[[e.cw_etype] for e in related])
        rset.req = cnx
        entity.cw_set_relation_cache(rtype, role, rset)


def fetch_relation_rqlst(
        cnx, entities, rtype, role, fetchattrs=None, force=False):
    if not force:
        entities = [
            e for e in entities if not e.cw_relation_cached(rtype, role)
        ]
    else:
        entities = list(entities)

    if not entities:
        return

    source_etypes = set(e.cw_etype for e in entities)
    rschema = cnx.vreg.schema.rschema(rtype)
    target_etypes = list(set(itertools.chain(
        *(rschema.targets(etype, role) for etype in source_etypes))))

    target_eschema = target_etypes[0]
    target_class = cnx.vreg['etypes'].etype_class(target_eschema)

    select = Select()
    mainvar = select.get_variable('X')
    select.add_selected(mainvar)

    if len(target_etypes) != 1:
        # Multiple target types possible. We will fetch only eid and
        # modification_date
        fetchattrs = cnx.vreg['etypes'].fetch_attrs(target_etypes)
        target_class._fetch_ambiguous_rtypes(
            select, mainvar, fetchattrs, target_etypes, cnx.vreg.schema)
    else:
        # Single target type
        if fetchattrs is None:
            fetchattrs = target_class.fetch_attrs

    target_class.fetch_rqlst(
        cnx.user, select, 'X', fetchattrs, settype=False)

    select.set_groupby(list(select.get_selected_variables()))

    srcvar = select.get_variable('Y')
    gr = Function('GROUP_CONCAT')
    gr.append(VariableRef(srcvar))
    # We need the source eids at a fixed index
    select.add_selected(gr, index=0)
    if role == 'subject':
        rel = make_relation(srcvar, rtype, (mainvar,), VariableRef)
    else:
        rel = make_relation(mainvar, rtype, (srcvar,), VariableRef)
    select.add_restriction(rel)

    select.add_restriction(
        make_constant_restriction(
            srcvar, 'eid', [e.eid for e in entities], 'Int'))

    return select
