# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
"""
Base export class
"""

from sqlalchemy import inspect
from sqlalchemy.orm import (
    ColumnProperty,
    RelationshipProperty,
)
from sqla_inspect.base import (
    BaseSqlaInspector,
    FormatterRegistry,
)
BLACKLISTED_KEYS = ()


# Should be completed (to see how this will be done)
FORMATTERS_REGISTRY = FormatterRegistry()


class BaseExporter():
    """
    A base exportation object, used to export tabular datas (csv or xls format)
    Should be used in conjunction with a writer
    """
    headers = []
    def __init__(self):
        self._datas = []

    @staticmethod
    def format_row(row):
        """
        Row formatter, should be implemented in subclasses
        """
        return row

    def add_row(self, row):
        """
            Add a row to our buffer
        """
        self._datas.append(self.format_row(row))

    def set_datas(self, datas):
        """
        bulk add rows
        """
        for data in datas:
            self.add_row(data)

    def render(self):
        """
        Render the datas as a file buffer
        """
        raise NotImplementedError()


def format_value(column_dict, value, key=None):
    """
    Format a value coming from the database (for example converts datetimes to
    strings)

    :param column_dict: The column datas collected during inspection
    :param value: A value coming from the database
    :param key: The exportation key
    """
    if column_dict['name'] == 'created_at':
        print("Formatting a value")
        print(value)

        print FORMATTERS_REGISTRY

    formatter = column_dict.get('formatter')
    prop = column_dict['__col__']

    res = value

    if value in ('', None,):
        res = ''

    elif formatter is not None:
        res = formatter(value)

    else:
        if hasattr(prop, "columns"):
            sqla_column = prop.columns[0]
            column_type = getattr(sqla_column.type, 'impl', sqla_column.type)

            formatter = FORMATTERS_REGISTRY.get_formatter(column_type, key)
            if formatter is not None:
                res = formatter(value)

    return res


class SqlaExporter(BaseExporter, BaseSqlaInspector):
    """
    Sqla exportation class
    Allow to stream datas to be exported

        config_key

            The key in the export subdict in the sqlalchemy Column's info dict that is used to
            configure this export
            e.g : set config_key = "csv" if your column configuration looks like
            the following:
            Column(Integer, info={'export' :
                {'csv': {<config>}},
                    <main_export_config>
                }

        .. note::

            By default, we look for the title in the colanderalchemy's title key
            info={'colanderalchemy': {'title': u'Column title'}}
    """
    config_key = ''

    def __init__(self, model):
        BaseExporter.__init__(self)
        BaseSqlaInspector.__init__(self, model)
        self.headers = self._collect_headers()

    def _collect_headers(self):
        """
        Collect headers from the models attribute info col
        """
        res = []

        for prop in self.get_sorted_columns():

            if prop.key in BLACKLISTED_KEYS:
                continue

            info_dict = self.get_info_field(prop)
            main_infos = info_dict.get('export', {}).copy()

            infos = main_infos.get(self.config_key, {})

            if infos.get('exclude', False) or main_infos.get('exclude', False):
                continue

            # By default, we use colanderalchemy's way of configuring titles
            title = info_dict.get('colanderalchemy', {}).get('title')

            if title is not None and not main_infos.has_key('label'):
                main_infos['label'] = title

            main_infos.setdefault('label', prop.key)

            main_infos['name'] = prop.key

            main_infos.update(infos)

            # We keep the original prop in case it's usefull
            main_infos['__col__'] = prop

            if isinstance(prop, RelationshipProperty):
                main_infos = self._collect_relationship(main_infos, prop, res)
                if not main_infos or not main_infos.has_key('related_key'):
                    # If still no success, we forgot this one
                    print("Maybe there's missing some informations \
about a relationship")
                    continue
            else:
                main_infos = self._merge_many_to_one_field_from_fkey(
                    main_infos, prop, res
                )
                if main_infos is None:
                    continue

            res.append(main_infos)
        return res

    def _collect_relationship(self, main_infos, prop, result):
        """
        collect a relationship header:
            * remove onetomany relationship
            * merge foreignkeys with associated manytoone rel if we were able to
                find an attribute that will represent the destination model
                (generally a label of a configurable option)

        :param dict main_infos: The already collected datas about this column
        :param obj prop: The property mapper of the relationship
        :param list result: The actual collected headers
        :returns: a dict with the datas matching this header
        """
        # No handling of the uselist relationships for the moment
        if prop.uselist:
            main_infos = None
        else:
            related_field_inspector = inspect(prop.mapper)

            self._merge_many_to_one_field(main_infos, prop, result)

            if not main_infos.has_key('related_key'):
                # If one of those keys exists in the corresponding
                # option, we use it as reference key
                for rel_key in ('label', 'name', 'title'):
                    if related_field_inspector.attrs.has_key(rel_key):
                        main_infos['related_key'] = rel_key
                        break
        return main_infos

    def _merge_many_to_one_field(self, main_infos, prop, result):
        """
        Find the associated id foreignkey and get the title from it
        Remove this fkey field from the export

        :param dict main_infos: The already collected datas about this column
        :param obj prop: The property mapper of the relationship
        :param list result: The actual collected headers
        :returns: a title
        """
        title = None
        # We first find the related foreignkey to get the good title
        rel_base = list(prop.local_columns)[0]
        related_fkey_name = rel_base.name
        for val in result:
            if val['name'] == related_fkey_name:
                title = val['label']
                main_infos['label'] = title
                result.remove(val)
                break

        return main_infos

    def _merge_many_to_one_field_from_fkey(self, main_infos, prop, result):
        """
        Find the relationship associated with this fkey and set the title

        :param dict main_infos: The already collected datas about this column
        :param obj prop: The property mapper of the relationship
        :param list result: The actual collected headers
        :returns: a main_infos dict or None
        """
        if prop.columns[0].foreign_keys and prop.key.endswith('_id'):
            # We have a foreign key, we'll try to merge it with the
            # associated foreign key
            rel_name = prop.key[0:-3]
            for val in result:
                if val["name"] == rel_name:
                    val["label"] = main_infos['label']
                    main_infos = None # We can forget this field in export
                    break
        return main_infos

    def add_row(self, obj):
        """
        fill a new row with the given obj

            obj

               instance of the exporter's model
        """
        row = {}
        for column in self.headers:

            if isinstance(column['__col__'], ColumnProperty):
                value = self._get_column_cell_val(obj, column)

            elif isinstance(column['__col__'], RelationshipProperty):
                value = self._get_relationship_cell_val(obj, column)

            row[column['name']] = value

        self._datas.append(self.format_row(row))

    def _get_formatted_val(self, obj, name, column):
        """
        Format the value of the attribute 'name' from the given object
        """
        val = getattr(obj, name, None)
        return format_value(column, val, self.config_key)

    def _get_relationship_cell_val(self, obj, column):
        """
        Return the value to insert in a relationship cell
        """
        name = column['name']
        related_key = column.get('related_key', 'label')

        related_obj = getattr(obj, name, None)

        if related_obj is None:
            return ""
        if column['__col__'].uselist: # OneToMany
            _vals = []
            for rel_obj in related_obj:
                _vals.append(
                    self._get_formatted_val(rel_obj, related_key, column)
                )
            val = '\n'.join(_vals)
        else:
            val = self._get_formatted_val(related_obj, related_key, column)

        return val

    def _get_column_cell_val(self, obj, column):
        """
        Return a value of a "column" cell
        """
        name = column['name']
        return self._get_formatted_val(obj, name, column)
