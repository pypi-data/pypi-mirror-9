import pytest

from rpython.conftest import option
from rpython.translator.translator import graphof as tgraphof
from rpython.flowspace.model import const
from rpython.flowspace.operation import CallOp
from rpython.annotator.annrpython import RPythonAnnotator
from rpython.translator.backendopt.inline import BaseInliner
from rpython.translator.simplify import simplify_graph


class Inliner(BaseInliner):
    def __init__(self, annotator, graph):
        BaseInliner.__init__(self, annotator.translator, graph, None,
                             can_raise=lambda op: op.can_raise)

    def exc_match(self, value, exitcase):
        pass

    def get_graph_from_op(self, op):
        func = op.args[0].value
        return tgraphof(self.translator, func)

    def search_for_calls(self, block):
        pass


class _Annotator(RPythonAnnotator):
    def build_types(self, *args):
        s = RPythonAnnotator.build_types(self, *args)
        if option.view:
            self.translator.view()
        return s

    def graphof(self, func):
        return tgraphof(self.translator, func)

    def check_inline(self, outer, inner):
        graph = self.graphof(outer)
        block, i = self.find_func(graph, inner)
        inliner = Inliner(self, graph)
        inliner.inline_once(block, i)
        simplify_graph(graph)
        if option.view:
            self.translator.view()

    def find_func(self, graph, func):
        for block in graph.iterblocks():
            for i in range(len(block.operations)):
                op = block.operations[i]
                if isinstance(op, CallOp) and op.args[0] == const(func):
                    return block, i


@pytest.fixture
def annotator():
    return _Annotator()


def test_inline_simple(annotator):
    def f(x, y):
        return (g(x, y) + 1) * x

    def g(x, y):
        if x > 0:
            return x * y
        else:
            return -x * y

    annotator.build_types(f, [int, int])
    eval_func = annotator.check_inline(f, g)
    result = eval_func([-1, 5])
    assert result == f(-1, 5)
    result = eval_func([2, 12])
    assert result == f(2, 12)


