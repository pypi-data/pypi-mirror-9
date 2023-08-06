# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
#

from sqla_inspect import export

def test_collect_keys():
    from sqla_inspect.tests.models import (Parent, Child)

    exporter = export.SqlaExporter(Parent)
    assert len(exporter.headers) == 2
    assert exporter.headers[0]['name'] == 'id'

    exporter = export.SqlaExporter(Child)
    assert len(exporter.headers) == 6
    headers_name = [h['name'] for h in exporter.headers]
    headers_keys = [h['key'] for h in exporter.headers]

    assert headers_keys == ['id', 'name', 'parent_id', 'parent', 'parent',
                            'friend']
    assert headers_name == ['id', 'name', 'parent_id', 'parent id',
                            'parent name', 'friend']
    assert "password" not in headers_name

    for i in exporter.headers:
        if i['label'] == 'Parent name':
            header_totest = i
    assert header_totest['label'] == 'Parent name'
    assert header_totest['related_key'] == 'name'


def test_format_entry():
    from sqla_inspect.tests.models import (Parent, Child, Friend)

    exporter = export.SqlaExporter(Child)

    model = Child(
        name=u"Éric",
        password="secret",
        id=5,
        parent_id=4,
        parent=Parent(id=4, name=u"Amédé")
    )
    exporter.add_row(model)

    row_datas = exporter._datas[0]

    assert row_datas['id'] == 5
    assert row_datas['name'] == u"Éric"
    assert row_datas['parent_id'] == 4
    assert row_datas['parent name'] == u"Amédé"
    assert row_datas['parent id'] == 4

    model.friend = Friend(
        id=5,
        name='Jenifer',
        aka='Jane',
    )
    exporter.add_row(model)

    row_datas = exporter._datas[1]

    assert row_datas['friend'] == u"Jane"
