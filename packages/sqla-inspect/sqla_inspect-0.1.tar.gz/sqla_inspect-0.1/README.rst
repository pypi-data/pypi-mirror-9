============================
SQLAlchemy inspection tools
============================

Provide tools for sqlalchemy models :

* inspection
* export (csv, excel, py3o context)
* import

requires:

openpyxl
py3o
colanderalchemy
SQLAlchemy

Export
======

.. code-block:: python

    from sqla_inspect.csv import SqlaCsvExporter

    exporter = SqlaCsvExporter(Model)
    for row in Model.query():
        exporter.add_row(row)
    exporter.render()

Customization
--------------

Globally
.........

You can globally set formatters through which value of a specific type will be
passed before export.

.. code-block::

    from sqla_inspect.export import FORMATTERS_REGISTRY
    FORMATTERS_REGISTRY.add_formatter(
        sqlalchemy.Boolean,
        lambda val: 'Y' and val or 'N'
    )

All booleans will be converted to 'Y' or 'N'. If you want to do this formatting
only for a specific export, add a key (the key as configured in the exporter
class, csv/excel/py3o for provided exporters)

.. code-block::

    from sqla_inspect.export import FORMATTERS_REGISTRY
    FORMATTERS_REGISTRY.add_formatter(
        sqlalchemy.Boolean,
        lambda val: 'Y' and val or 'N',
        'csv'
    )

You can globally blacklist some fields to avoid exporting them

.. code-block::

    from sqla_inspect.export import BLACKLISTED_KEYS
    BLACKLISTED_KEYS = ('_acl', 'password')


Per Column
..........

You can customize columns informations:

* The header label through the 'label' key
* The way a relationship is exported through the 'related_key' (the attribute on
  the related object)
* The way the datas is formatted providing a formatter under the 'formatter' key
* Exclude a column setting the 'exclude' key

All this keys can be set at differente levels:

If you want to customize the header labels, you can provide informations in the
export/csv key

.. code-block:: python

    class Model(Base):
        attr1 = Column(
            Integer,
            info={'export': {'csv': {'label': u'My custom header'}}}
        )


If not set it will look one level higher in the export key

.. code-block:: python

    class Model(Base):
        attr1 = Column(
            Integer,
            info={'export': {'label': u'My custom header'}}
        )

If not set, only in the case of labels, it will look into the colanderalchemy
'title' attribute.

The same things can be done with the excel.SqlaXlsExporter class (that shares
the export dict with the SqlaCsvExporter.

LIMITATIONS
------------

Relationship that point to lists are not handled.
