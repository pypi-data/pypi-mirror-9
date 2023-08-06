# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
#
"""
utilities to inspect Sqlalchemy models
"""
from sqlalchemy import inspect
from sqlalchemy.orm import (
    ColumnProperty,
    RelationshipProperty,
)
from colanderalchemy.schema import _creation_order


class BaseSqlaInspector(object):
    """
    Base class for exporters
    """
    def __init__(self, model):
        self.inspector = inspect(model)

    def get_sorted_columns(self):
        """
        Return columns regarding their relevance in the model's declaration
        """
        return sorted(self.inspector.attrs, key=_creation_order)

    def get_columns_only(self):
        """
        Return only the columns
        """
        return [prop for prop in self.get_sorted_columns() \
                if isinstance(prop, ColumnProperty)]

    def get_relationships_only(self):
        """
        Return only the relationships
        """
        return [prop for prop in self.get_sorted_columns() \
                if isinstance(prop, RelationshipProperty)]

    @staticmethod
    def get_info_field(prop):
        """
        Return the info attribute of the given property
        """
        if isinstance(prop, ColumnProperty):
            column = prop.columns[0]

        elif isinstance(prop, RelationshipProperty):
            column = prop

        return column.info


class FormatterRegistry(dict):
    """
    A registry used to store sqla columns <-> formatters association
    """
    def add_formatter(self, sqla_col_type, formatter, key_specific=None):
        """
        Add a formatter to the registry
        if key_specific is provided, this formatter will only be used for some
        specific exports
        """
        if key_specific is not None:
            self.setdefault(key_specific, {})[sqla_col_type] = formatter
        else:
            self[sqla_col_type] = formatter

    def get_formatter(self, sqla_col, key_specific=None):
        formatter = None
        if key_specific is not None:
            formatter = self.get(key_specific, {}).get(sqla_col.__class__)

        if formatter is None:
            formatter = self.get(sqla_col.__class__)

        return formatter

