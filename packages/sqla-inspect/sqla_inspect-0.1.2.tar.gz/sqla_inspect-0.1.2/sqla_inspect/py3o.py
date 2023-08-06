# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
"""
Py3o exporters


>>> model = Company.query().first()
>>> template = Template.query().first()
>>> odt_file_datas = compile_template(model, template.data_obj)
"""
from __future__ import absolute_import
from cStringIO import StringIO

from sqlalchemy.orm import (
    ColumnProperty,
    RelationshipProperty,
)
from sqlalchemy import (
    Date,
    DateTime,
)
from genshi.core import Markup

from py3o.template import Template

from sqla_inspect.base import (
    BaseSqlaInspector,
)
from sqla_inspect.export import (
    format_value,
)


def format_py3o_val(value):
    """
    format a value to fit py3o's context

    * Handle linebreaks
    """
    return Markup(unicode(value).replace(u'\n', u'<text:line-break/>'))


class SqlaContext(BaseSqlaInspector):
    """
    Provide a tool to build a context dict based on a given model. The datas are
    built following the informations retrieved from the model's declaration.

    Custom configuration can be achieved by customizing the info dict attribute
    from each column.

        config_key

            The key in the info dict we will look for.

            Actually handles the following informations :
                exclude : should the column be excluded from the output
                name : the key in the resulting dict


    >>> serializer = SqlaContext(Company)
    >>> company = Company.get(263)
    >>> res = s.compile_obj(company)


    :param model: a SQLA model
    """
    config_key = 'py3o'

    def __init__(self, model, rels=None):
        BaseSqlaInspector.__init__(self, model)
        # We store the relations already treated by storing the primaryjoin that
        # they use, since the backref uses the same join string, we can avoid
        # recursive collection
        self.rels = rels or []
        self.columns = self.collect_columns()

    def collect_columns(self):
        """
        Collect columns information from a given model.

        a column info contains

            the py3 informations

                exclude

                    Should the column be excluded from the current context ?

                name

                    the name of the key in the resulting py3o context of the
                    column

            __col__

                The original column object

            __prop__

                In case of a relationship, the SqlaContext wrapping the given
                object

        """
        res = []
        for prop in self.get_sorted_columns():

            info_dict = self.get_info_field(prop)
            export_infos = info_dict.get('export', {}).copy()

            main_infos = export_infos.get(self.config_key, {}).copy()

            if export_infos.get('exclude', False) or main_infos.get('exclude',
                                                                    False):
                continue

            infos = export_infos
            infos.update(main_infos)

            # Si la clé name n'est pas définit on la met au nom de la colonne
            # par défaut
            infos.setdefault('name', prop.key)
            infos['__col__'] = prop
            if isinstance(prop, RelationshipProperty):
                join = str(prop.primaryjoin)
                if join in self.rels:
                    continue
                else:
                    self.rels.append(str(join))
                    infos['__prop__'] = SqlaContext(
                        prop.mapper,
                        rels=self.rels[:]
                    )

            res.append(infos)
        return res

    def compile_obj(self, obj):
        """
        generate a context based on the given obj

        :param obj: an instance of the model
        """
        res = {}
        for column in self.columns:
            if isinstance(column['__col__'], ColumnProperty):
                value = getattr(obj, column['__col__'].key, None)

                value = format_value(column, value, self.config_key)

                value = format_py3o_val(value)

            elif isinstance(column['__col__'], RelationshipProperty):
                # 1- si la relation est directe (une AppOption), on override le
                # champ avec la valeur (pour éviter des profondeurs)
                # 2- si l'objet lié est plus complexe, on lui fait son propre
                # chemin
                # 3- si la relation est uselist, on fait une liste d'élément
                # liés qu'on place dans une clé "l" et on place l'élément lié
                # dans une clé portant le nom de son index
                related = getattr(obj, column['__col__'].key)
                if column['__col__'].uselist:
                    value = {'l': []}
                    for index, rel_obj in enumerate(related):
                        compiled_res = column['__prop__'].compile_obj(rel_obj)
                        value[str(index)] = compiled_res
                        value['l'].append(compiled_res)

                else:
                    value = column['__prop__'].compile_obj(related)

            res[column['name']] = value

        return res


def get_compilation_context(instance):
    """
    Return the compilation context for py3o templating

    Build a deep dict representation of the given instance and add config values

    :param obj instance: a SQLAlchemy model instance
    :return: a multi level dict with context datas
    :rtype: dict
    """
    context_builder = SqlaContext(instance.__class__)
    py3o_context = context_builder.compile_obj(instance)
    return py3o_context


def compile_template(instance, template, additionnal_context=None):
    """
    Fill the given template with the instance's datas and return the odt file

    For every instance class, common values are also inserted in the context
    dict (and so can be used) :

        * config values

    :param obj instance: the instance of a model (like Userdatas, Company)
    :param template: the template object to use
    :param dict additionnal_context: A dict containing datas we'd like to ass to
    the py3o compilation template
    :return: a stringIO object filled with the resulting odt's informations
    """
    py3o_context = get_compilation_context(instance)

    if additionnal_context is not None:
        py3o_context.update(additionnal_context)

    output_doc = StringIO()

    odt_builder = Template(template, output_doc)
    odt_builder.render(py3o_context)

    return output_doc
