# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>

from sqla_inspect.base import FormatterRegistry


class Dummy(object):
    pass

def dummy_func(a):
    return a

def test_registry():
    f = FormatterRegistry()
    assert f.get_formatter(Dummy()) is None

    f.add_formatter(Dummy, dummy_func)
    assert f.get_formatter(Dummy()) is dummy_func
    assert f.get_formatter(Dummy(), 'non_existingkey') is dummy_func

    f = FormatterRegistry()
    f.add_formatter(Dummy, dummy_func, 'key')
    assert f.get_formatter(Dummy(), 'key') is dummy_func
    assert f.get_formatter(Dummy()) is None

