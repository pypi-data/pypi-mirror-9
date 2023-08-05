
"""
A parser for the algebraic formulas used to specify a query to ALPACA.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"

import numpy as np

from alpaca.utils import AlpacaError


def parse(expression, samples):
    identifiers = {
        sample: SampleUnion(sample) for sample in samples
    }
    return eval(expression, identifiers)


def get_samples(formula):
    # provide inorder traversal of sample ids but do not repeat them
    def _get_samples(node):
        if isinstance(node, SampleUnion):
            yield from node.children
        else:
            for child in node.children:
                yield from _get_samples(child)
    return list(_get_samples(formula))


class AlgebraNode:

    operator = None

    def __add__(self, other):
        return Union(self, other)

    def __sub__(self, other):
        return Difference(self, other)

    def __mul__(self, other):
        return RelaxedIntersection(self, other)

    def __call__(self, **params):
        raise AlpacaError("Syntax error in query: params can be only given for unions of samples, single samples or relaxed intersections.")

    def __str__(self):
        s = self.operator.join(map(str, self.children))
        if len(self.children) > 1:
            s = "({})".format(s)
        return s


class ParamNode(AlgebraNode):
    param_names = {}

    def __init__(self, *children):
        self.children = list(children)
        self.params = {}

    def check(self, **params):
        pass

    def __call__(self, **params):
        self.check(**params)
        if not self.param_names >= params.keys():
            raise AlpacaError(
                "Only the following parameters are allowed in "
                "the query:\n{}".format(self.param_names)
            )
        self.params = params
        return self

    def __str__(self):
        return "{}[{}]".format(
            super().__str__(self),
            ", ".join("{}={}".format(k, v) for k, v in self.params.items())
        )


class SampleUnion(ParamNode):
    param_names = {"het"}

    def __init__(self, *children):
        self.children = list(children)
        self.params = {}

    @property
    def heterozygosity(self):
        return self.params.get("het", None)

    def __add__(self, other):
        if isinstance(other, SampleUnion):
            if self.params != other.params:
                return Union(self, other)
            old = set(self.children)
            return SampleUnion(*(
                self.children +
                [child for child in other.children if child not in old]
            ))
        else:
            return Union(self, other)


class Union(AlgebraNode):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return "({})".format(" + ".join(map(str, self.children)))


class Difference(AlgebraNode):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return "({})".format(" - ".join(map(str, self.children)))


class RelaxedIntersection(ParamNode):
    param_names = {"k", "het"}
    syntax_error = AlpacaError(
        "Syntax error in query: relaxed intersection is an operator "
        "between samples only."
    )

    def __init__(self, *children):
        self.children = list(children)
        self.params = {}

    @property
    def heterozygosity(self):
        return self.params.get("het", None)

    @property
    def k(self):
        return self.params.get("k", None)

    def check(self, **params):
        if "k" in params and params["k"] > len(self.children):
            raise AlpacaError(
                "Syntax error in query: k param for relaxed intersection may not "
                "exceed the number of involved samples."
            )

    def __mul__(self, other):
        if isinstance(other, SampleUnion):
            if len(other.children) != 1:
                raise self.syntax_error
            child, = other.children
            if child not in self.children:
                self.children.append(child)
            return self
        else:
            raise self.syntax_error
