"""
This module contains various auxiliary functions which are used throughout the library.
"""

from __future__ import division

import functools
import itertools
import collections
import os.path
import warnings
import inspect
import funcsigs

from mako.template import Template


class Graph:

    def __init__(self, pairs=None):
        self._pairs = set()
        self._nodes = collections.defaultdict(set)
        if pairs is not None:
            self.add_edges(pairs)

    def add_edge(self, node1, node2):
        assert node1 != node2
        self._nodes[node1].add(node2)
        self._nodes[node2].add(node1)
        self._pairs.add(tuple(sorted((node1, node2))))

    def add_edges(self, pairs):
        for node1, node2 in pairs:
            self.add_edge(node1, node2)

    def add_graph(self, graph):
        for node1, node2 in graph.pairs():
            self.add_edge(node1, node2)

    def add_cluster(self, nodes):
        self.add_edges(itertools.combinations(nodes, 2))

    def remove_node(self, node):
        deps = self._nodes[node]
        for dep in deps:
            self._nodes[dep].remove(node)
            self._pairs.remove(tuple(sorted((node, dep))))
        del self._nodes[node]

    def remove_edge(self, node1, node2):
        assert node1 != node2
        self._pairs.remove(tuple(sorted((node1, node2))))

        self._nodes[node1].remove(node2)
        if len(self._nodes[node1]) == 0:
            del self._nodes[node1]

        self._nodes[node2].remove(node1)
        if len(self._nodes[node2]) == 0:
            del self._nodes[node2]

    def __getitem__(self, node):
        return self._nodes[node]

    def pairs(self):
        return self._pairs

    def translate(self, translator):
        pairs = []
        for node1, node2 in self._pairs:
            pairs.append(tuple(sorted((translator(node1), translator(node2)))))
        return Graph(pairs)


def product(seq):
    """
    Returns the product of elements in the iterable ``seq``.
    """
    return functools.reduce(lambda x1, x2: x1 * x2, seq, 1)


def make_template(template, filename=False):
    # Can't import submodules from reikna itself here, because it creates circular dependencies
    # (computation modules have template_for() calls at the root level,
    # so they get activated on import).
    kwds = dict(
        future_imports=['division'],
        strict_undefined=True,
        imports=['import numpy'])

    # Creating a template from a filename results in more comprehensible stack traces,
    # so we are taking advantage of this if possible.
    if filename:
        kwds['filename'] = template
        return Template(**kwds)
    else:
        return Template(template, **kwds)


def template_from(template):
    """
    Creates a Mako template object from a given string.
    If ``template`` already has ``render()`` method, does nothing.
    """
    if hasattr(template, 'render'):
        return template
    else:
        return make_template(template)


def extract_signature_and_value(func_or_str, default_parameters=None):
    if not inspect.isfunction(func_or_str):
        if default_parameters is None:
            parameters = []
        else:
            kind = funcsigs.Parameter.POSITIONAL_OR_KEYWORD
            parameters = [funcsigs.Parameter(name, kind=kind) for name in default_parameters]

        return funcsigs.Signature(parameters), func_or_str

    signature = funcsigs.signature(func_or_str)

    # pass mock values to extract the value
    args = [None] * len(signature.parameters)
    return signature, func_or_str(*args)


def template_def(signature, code):
    """
    Returns a ``Mako`` template with the given ``signature``.

    :param signature: a list of postitional argument names,
        or a ``Signature`` object from ``funcsigs`` module.
    :code: a body of the template.
    """
    if not isinstance(signature, funcsigs.Signature):
        # treating ``signature`` as a list of positional arguments
        # HACK: Signature or Parameter constructors are not documented.
        kind = funcsigs.Parameter.POSITIONAL_OR_KEYWORD
        signature = funcsigs.Signature([funcsigs.Parameter(name, kind=kind) for name in signature])

    template_src = "<%def name='_func" + str(signature) + "'>\n" + code + "\n</%def>"
    return template_from(template_src).get_def('_func')


def template_for(filename):
    """
    Returns the Mako template object created from the file
    which has the same name as ``filename`` and the extension ``.mako``.
    Typically used in computation modules as ``template_for(__filename__)``.
    """
    name, _ext = os.path.splitext(os.path.abspath(filename))
    return make_template(name + '.mako', filename=True)


def min_blocks(length, block):
    """
    Returns minimum number of blocks with length ``block``
    necessary to cover the array with length ``length``.
    """
    return (length - 1) // block + 1


def log2(num):
    """
    Integer-valued logarigthm with base 2.
    If ``n`` is not a power of 2, the result is rounded to the smallest number.
    """
    pos = 0
    for pow_ in [16, 8, 4, 2, 1]:
        if num >= 2 ** pow_:
            num //= (2 ** pow_)
            pos += pow_
    return pos


def bounding_power_of_2(num):
    """
    Returns the minimal number of the form ``2**m`` such that it is greater or equal to ``n``.
    """
    if num == 1:
        return 1
    else:
        return 2 ** (log2(num - 1) + 1)


def factors(num, limit=None):
    """
    Returns the list of pairs ``(factor, num/factor)`` for all factors of ``num``
    (including 1 and ``num``), sorted by ``factor``.
    If ``limit`` is set, only pairs with ``factor <= limit`` are returned.
    """
    if limit is None or limit > num:
        limit = num

    float_sqrt = num ** 0.5
    int_sqrt = int(round(float_sqrt))

    result = []

    if int_sqrt ** 2 == num:
        int_limit = int_sqrt + 1
    else:
        int_limit = int(float_sqrt) + 1

    for i in range(1, int_limit):
        div, mod = divmod(num, i)
        if mod == 0:
            result.append((i, div))

    if limit > result[-1][0]:
        if int_sqrt ** 2 == num:
            to_rev = result[:-1]
        else:
            to_rev = result

        result = result + [(div, f) for f, div in reversed(to_rev)]

    return [r for r in result if r[0] <= limit]


def wrap_in_tuple(seq_or_elem):
    """
    If ``seq_or_elem`` is a sequence, converts it to a ``tuple``,
    otherwise returns a tuple with a single element ``seq_or_elem``.
    """
    if seq_or_elem is None:
        return tuple()
    elif isinstance(seq_or_elem, str):
        return (seq_or_elem,)
    elif isinstance(seq_or_elem, collections.Iterable):
        return tuple(seq_or_elem)
    else:
        return (seq_or_elem,)


class ignore_integer_overflow():
    """
    Context manager for ignoring integer overflow in numpy operations on scalars
    (not ignored by default because of a bug in numpy).
    """

    def __init__(self):
        self.catch = warnings.catch_warnings()

    def __enter__(self):
        self.catch.__enter__()
        warnings.filterwarnings("ignore", "overflow encountered in uint_scalars")
        warnings.filterwarnings("ignore", "overflow encountered in ulong_scalars")

    def __exit__(self, *args, **kwds):
        self.catch.__exit__(*args, **kwds)
