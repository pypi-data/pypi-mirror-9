#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from collections import namedtuple
from sql import operators, Column, Literal, Select, CombiningQuery
from sql.conditionals import Coalesce, NullIf
from sql.operators import Concat

from trytond.pyson import PYSON
from trytond.const import OPERATORS
from trytond.transaction import Transaction
from trytond.pool import Pool


def domain_validate(value):
    assert isinstance(value, list), 'domain must be a list'

    def test_domain(dom):
        for arg in dom:
            if isinstance(arg, basestring):
                if arg not in ('AND', 'OR'):
                    return False
            elif (isinstance(arg, tuple)
                or (isinstance(arg, list)
                    and len(arg) > 2
                    and ((arg[1] in OPERATORS)
                        or (isinstance(arg[1], PYSON)
                            and arg[1].types() == set([str]))))):
                pass
            elif isinstance(arg, list):
                if not test_domain(arg):
                    return False
        return True
    assert test_domain(value), 'invalid domain'


def states_validate(value):
    assert isinstance(value, dict), 'states must be a dict'
    for state in value:
        if state == 'icon':
            continue
        assert isinstance(value[state], (bool, PYSON)), \
            'values of states must be PYSON'
        if hasattr(value[state], 'types'):
            assert value[state].types() == set([bool]), \
                'values of states must return boolean'


def on_change_validate(value):
    if value:
        assert isinstance(value, list), 'on_change must be a list'


def on_change_with_validate(value):
    if value:
        assert isinstance(value, list), 'on_change_with must be a list'


def depends_validate(value):
    assert isinstance(value, list), 'depends must be a list'


def context_validate(value):
    assert isinstance(value, dict), 'context must be a dict'


def size_validate(value):
    if value is not None:
        assert isinstance(value, (int, PYSON)), 'size must be PYSON'
        if hasattr(value, 'types'):
            assert value.types() == set([int]), \
                'size must return integer'

SQL_OPERATORS = {
    '=': operators.Equal,
    '!=': operators.NotEqual,
    'like': operators.Like,
    'not like': operators.NotLike,
    'ilike': operators.ILike,
    'not ilike': operators.NotILike,
    'in': operators.In,
    'not in': operators.NotIn,
    '<=': operators.LessEqual,
    '>=': operators.GreaterEqual,
    '<': operators.Less,
    '>': operators.Greater,
    }


class Field(object):
    _type = None

    def __init__(self, string='', help='', required=False, readonly=False,
            domain=None, states=None, select=False, on_change=None,
            on_change_with=None, depends=None, context=None,
            loading='eager'):
        '''
        :param string: A string for label of the field.
        :param help: A multi-line help string.
        :param required: A boolean if ``True`` the field is required.
        :param readonly: A boolean if ``True`` the field is not editable in
            the user interface.
        :param domain: A list that defines a domain constraint.
        :param states: A dictionary. Possible keys are ``required``,
            ``readonly`` and ``invisible``. Values are pyson expressions that
            will be evaluated with record values. This allows to change
            dynamically the attributes of the field.
        :param select: An boolean. When True search will be optimized.
        :param on_change: A list of values. If set, the client will call the
            method ``on_change_<field_name>`` when the user changes the field
            value. It then passes this list of values as arguments to the
            function.
        :param on_change_with: A list of values. Like ``on_change``, but
            defined the other way around. The list contains all the fields that
            must update the current field.
        :param depends: A list of field name on which this one depends.
        :param context: A dictionary which will be given to open the relation
            fields.
        :param loading: Define how the field must be loaded:
            ``lazy`` or ``eager``.
        '''
        assert string, 'a string is required'
        self.string = string
        self.help = help
        self.required = required
        self.readonly = readonly
        self.__domain = None
        self.domain = domain or []
        self.__states = None
        self.states = states or {}
        self.select = bool(select)
        self.__on_change = None
        self.on_change = on_change
        self.__on_change_with = None
        self.on_change_with = on_change_with
        self.__depends = None
        self.depends = depends or []
        self.__context = None
        self.context = context or {}
        assert loading in ('lazy', 'eager'), \
            'loading must be "lazy" or "eager"'
        self.loading = loading
        self.name = None

    def _get_domain(self):
        return self.__domain

    def _set_domain(self, value):
        domain_validate(value)
        self.__domain = value

    domain = property(_get_domain, _set_domain)

    def _get_states(self):
        return self.__states

    def _set_states(self, value):
        states_validate(value)
        self.__states = value

    states = property(_get_states, _set_states)

    def _get_on_change(self):
        return self.__on_change

    def _set_on_change(self, value):
        on_change_validate(value)
        self.__on_change = value
    on_change = property(_get_on_change, _set_on_change)

    def _get_on_change_with(self):
        return self.__on_change_with

    def _set_on_change_with(self, value):
        on_change_with_validate(value)
        self.__on_change_with = value

    on_change_with = property(_get_on_change_with, _set_on_change_with)

    def _get_depends(self):
        return self.__depends

    def _set_depends(self, value):
        depends_validate(value)
        self.__depends = value

    depends = property(_get_depends, _set_depends)

    def _get_context(self):
        return self.__context

    def _set_context(self, value):
        context_validate(value)
        self.__context = value

    context = property(_get_context, _set_context)

    def __get__(self, inst, cls):
        if inst is None:
            return self
        assert self.name is not None
        return inst.__getattr__(self.name)

    def __set__(self, inst, value):
        assert self.name is not None
        if inst._values is None:
            inst._values = {}
        inst._values[self.name] = value

    @staticmethod
    def sql_format(value):
        return value

    def sql_type(self):
        raise NotImplementedError

    def _domain_value(self, operator, value):
        if isinstance(value, (Select, CombiningQuery)):
            return value
        if operator in ('in', 'not in'):
            return [self.sql_format(v) for v in value if v is not None]
        else:
            return self.sql_format(value)

    def _domain_add_null(self, column, operator, value, expression):
        if operator in ('in', 'not in'):
            if (not isinstance(value, (Select, CombiningQuery))
                    and any(v is None for v in value)):
                if operator == 'in':
                    expression |= (column == None)
                else:
                    expression &= (column != None)
        return expression

    def convert_domain(self, domain, tables, Model):
        "Return a SQL expression for the domain using tables"
        table, _ = tables[None]
        name, operator, value = domain
        Operator = SQL_OPERATORS[operator]
        column = Column(table, name)
        expression = Operator(column, self._domain_value(operator, value))
        if isinstance(expression, operators.In) and not expression.right:
            expression = Literal(False)
        elif isinstance(expression, operators.NotIn) and not expression.right:
            expression = Literal(True)
        expression = self._domain_add_null(column, operator, value, expression)
        return expression

    def convert_order(self, name, tables, Model):
        "Return a SQL expression to order"
        table, _ = tables[None]
        method = getattr(Model, 'order_%s' % name, None)
        if method:
            return method(tables)
        else:
            return [Column(table, name)]


class FieldTranslate(Field):

    def __get_translation_join(self, Model, name,
            translation, model, table):
        language = Transaction().language
        if Model.__name__ == 'ir.model':
            return table.join(translation, 'LEFT',
                condition=(translation.name == Concat(Concat(
                            table.model, ','), name))
                & (translation.res_id == -1)
                & (translation.lang == language)
                & (translation.type == 'model')
                & (translation.fuzzy == False))
        elif Model.__name__ == 'ir.model.field':
            if name == 'field_description':
                type_ = 'field'
            else:
                type_ = 'help'
            return table.join(model, 'LEFT',
                condition=model.id == table.model).join(
                    translation, 'LEFT',
                    condition=(translation.name == Concat(Concat(
                                model.model, ','), table.name))
                    & (translation.res_id == -1)
                    & (translation.lang == language)
                    & (translation.type == type_)
                    & (translation.fuzzy == False))
        else:
            return table.join(translation, 'LEFT',
                condition=(translation.res_id == table.id)
                & (translation.name == '%s,%s' % (Model.__name__, name))
                & (translation.lang == language)
                & (translation.type == 'model')
                & (translation.fuzzy == False))

    def convert_domain(self, domain, tables, Model):
        pool = Pool()
        Translation = pool.get('ir.translation')
        IrModel = pool.get('ir.model')
        if not self.translate:
            return super(FieldTranslate, self).convert_domain(
                domain, tables, Model)

        table = Model.__table__()
        translation = Translation.__table__()
        model = IrModel.__table__()
        name, operator, value = domain
        join = self.__get_translation_join(Model, name,
            translation, model, table)
        Operator = SQL_OPERATORS[operator]
        column = Coalesce(NullIf(translation.value, ''),
            Column(table, name))
        where = Operator(column, self._domain_value(operator, value))
        if isinstance(where, operators.In) and not where.right:
            where = Literal(False)
        elif isinstance(where, operators.NotIn) and not where.right:
            where = Literal(True)
        where = self._domain_add_null(column, operator, value, where)
        return tables[None][0].id.in_(join.select(table.id, where=where))

    def convert_order(self, name, tables, Model):
        pool = Pool()
        Translation = pool.get('ir.translation')
        IrModel = pool.get('ir.model')
        if not self.translate:
            return super(FieldTranslate, self).convert_order(name, tables,
                Model)

        table, _ = tables[None]
        key = name + '.translation'
        if key not in tables:
            translation = Translation.__table__()
            model = IrModel.__table__()
            join = self.__get_translation_join(Model, name,
                translation, model, table)
            if join.left == table:
                tables[key] = {
                    None: (join.right, join.condition),
                    }
            else:
                tables[key] = {
                    None: (join.left.right, join.left.condition),
                    'translation': {
                        None: (join.right, join.condition),
                        },
                    }
        else:
            if 'translation' not in tables[key]:
                translation, _ = tables[key][None]
            else:
                translation, _ = tables[key]['translation'][None]

        return [Coalesce(NullIf(translation.value, ''), Column(table, name))]

SQLType = namedtuple('SQLType', 'base type')
