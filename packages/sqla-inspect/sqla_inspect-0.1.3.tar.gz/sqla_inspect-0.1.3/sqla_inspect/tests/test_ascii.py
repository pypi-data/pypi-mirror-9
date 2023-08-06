# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>

from sqla_inspect import ascii

def test_force_unicode():
    assert ascii.force_unicode(u"éko") == u"éko"
    assert ascii.force_unicode("éko") == u"éko"


def test_force_utf8():
    assert ascii.force_utf8(u"éko") == "éko"
    assert ascii.force_utf8("éko") == "éko"

def test_force_ascii():
    assert ascii.force_ascii("éko") == "eko"
    assert ascii.force_ascii(u"éko") == "eko"

def test_camel_case_to_name():
    assert ascii.camel_case_to_name("BaseObject") == "base_object"
    assert ascii.camel_case_to_name("BBaseObject") == "b_base_object"
