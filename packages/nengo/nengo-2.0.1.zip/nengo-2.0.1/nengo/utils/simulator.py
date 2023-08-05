from collections import defaultdict
import itertools

from .compat import iteritems
from .graphs import add_edges
from .stdlib import groupby


def operator_depencency_graph(operators):  # noqa: C901
    dg = defaultdict(set)

    for op in operators:
        add_edges(dg, itertools.product(op.reads + op.updates, [op]))
        add_edges(dg, itertools.product([op], op.sets + op.incs))
        # -- If a node is not connected to anything else, its ops won't be
        #    added through add_edges. We add them explicitly here instead.
        if op not in dg:
            dg[op] = set()

    # -- all views of a base object in a particular dictionary
    by_base_writes = defaultdict(list)
    by_base_reads = defaultdict(list)
    reads = defaultdict(list)
    sets = defaultdict(list)
    incs = defaultdict(list)
    ups = defaultdict(list)

    for op in operators:
        for node in op.sets + op.incs:
            by_base_writes[node.base].append(node)

        for node in op.reads:
            by_base_reads[node.base].append(node)

        for node in op.reads:
            reads[node].append(op)

        for node in op.sets:
            sets[node].append(op)

        for node in op.incs:
            incs[node].append(op)

        for node in op.updates:
            ups[node].append(op)

    validate_ops(sets, ups, incs)

    # -- Scheduling algorithm for serial evaluation:
    #    1) All sets on a given base signal
    #    2) All incs on a given base signal
    #    3) All reads on a given base signal
    #    4) All updates on a given base signal

    # -- incs depend on sets
    for node, post_ops in iteritems(incs):
        pre_ops = list(sets[node])
        for other in by_base_writes[node.base]:
            pre_ops.extend(sets[other])
        add_edges(dg, itertools.product(set(pre_ops), post_ops))

    # -- reads depend on writes (sets and incs)
    for node, post_ops in iteritems(reads):
        pre_ops = sets[node] + incs[node]
        for other in by_base_writes[node.base]:
            pre_ops.extend(sets[other] + incs[other])
        add_edges(dg, itertools.product(set(pre_ops), post_ops))

    # -- updates depend on reads, sets, and incs.
    for node, post_ops in iteritems(ups):
        pre_ops = sets[node] + incs[node] + reads[node]
        for other in by_base_writes[node.base]:
            pre_ops.extend(sets[other] + incs[other] + reads[other])
        for other in by_base_reads[node.base]:
            pre_ops.extend(sets[other] + incs[other] + reads[other])
        add_edges(dg, itertools.product(set(pre_ops), post_ops))

    return dg


def validate_ops(sets, ups, incs):
    # -- assert that only one op sets any particular view
    for node in sets:
        assert len(sets[node]) == 1, (node, sets[node])

    # -- assert that only one op updates any particular view
    for node in ups:
        assert len(ups[node]) == 1, (node, ups[node])

    # --- assert that any node that is incremented is also set/updated
    for node in incs:
        assert len(sets[node] + ups[node]) > 0, (node)

    # -- assert that no two views are both set and aliased
    for _, base_group in groupby(sets, lambda x: x.base, hashable=True):
        for node, other in itertools.combinations(base_group, 2):
            assert not node.shares_memory_with(other), (
                "%s shares memory with %s" % (node, other))

    # -- assert that no two views are both updated and aliased
    for _, base_group in groupby(ups, lambda x: x.base, hashable=True):
        for node, other in itertools.combinations(base_group, 2):
            assert not node.shares_memory_with(other), (
                "%s shares memory with %s" % (node, other))
