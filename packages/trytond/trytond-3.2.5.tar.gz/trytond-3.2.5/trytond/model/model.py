#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import copy
import collections
import warnings

from trytond.model import fields
from trytond.error import WarningErrorMixin
from trytond.pool import Pool, PoolBase
from trytond.pyson import PYSONEncoder
from trytond.transaction import Transaction
from trytond.url import URLMixin
from trytond.rpc import RPC

__all__ = ['Model']


class Model(WarningErrorMixin, URLMixin, PoolBase):
    """
    Define a model in Tryton.
    """
    _rec_name = 'name'

    id = fields.Integer('ID', readonly=True)

    @classmethod
    def __setup__(cls):
        super(Model, cls).__setup__()
        cls.__rpc__ = {
            'default_get': RPC(),
            'fields_get': RPC(),
            'on_change_with': RPC(instantiate=0),
            'pre_validate': RPC(instantiate=0),
            }
        cls._error_messages = {}

        if hasattr(cls, '__depend_methods'):
            cls.__depend_methods = cls.__depend_methods.copy()
        else:
            cls.__depend_methods = collections.defaultdict(set)

        # Copy fields and update depends
        for attr in dir(cls):
            if attr.startswith('_'):
                continue
            if not isinstance(getattr(cls, attr), fields.Field):
                continue
            field_name = attr
            field = copy.deepcopy(getattr(cls, field_name))
            setattr(cls, field_name, field)

            for attribute in ('on_change', 'on_change_with', 'autocomplete',
                    'selection_change_with'):
                if attribute == 'selection_change_with':
                    if isinstance(
                            getattr(field, 'selection', None), basestring):
                        function_name = field.selection
                    else:
                        continue
                else:
                    function_name = '%s_%s' % (attribute, field_name)
                function = getattr(cls, function_name, None)
                if function:
                    if getattr(function, 'depends', None):
                        setattr(field, attribute,
                            getattr(field, attribute) | function.depends)
                    if getattr(function, 'depend_methods', None):
                        cls.__depend_methods[(field_name, attribute)] |= \
                            function.depend_methods

    @classmethod
    def __post_setup__(cls):
        super(Model, cls).__post_setup__()

        # Set _fields
        cls._fields = {}
        for attr in dir(cls):
            if attr.startswith('_'):
                continue
            if isinstance(getattr(cls, attr), fields.Field):
                cls._fields[attr] = getattr(cls, attr)

        # Set _defaults
        cls._defaults = {}
        fields_names = cls._fields.keys()
        for field_name in fields_names:
            default_method = getattr(cls, 'default_%s' % field_name, False)
            if isinstance(default_method, collections.Callable):
                cls._defaults[field_name] = default_method

        for k in cls._defaults:
            assert k in cls._fields, \
                'Default function defined in %s but field %s does not exist!' \
                % (cls.__name__, k,)

        # Update __rpc__
        for field_name, field in cls._fields.iteritems():
            if isinstance(field, (fields.Selection, fields.Reference)) \
                    and not isinstance(field.selection, (list, tuple)) \
                    and field.selection not in cls.__rpc__:
                instantiate = 0 if field.selection_change_with else None
                cls.__rpc__.setdefault(field.selection,
                    RPC(instantiate=instantiate))

            for attribute in ('on_change', 'on_change_with', 'autocomplete'):
                function_name = '%s_%s' % (attribute, field_name)
                if getattr(cls, function_name, None):
                    cls.__rpc__.setdefault(function_name, RPC(instantiate=0))

        # Update depend on methods
        for (field_name, attribute), others in (
                cls.__depend_methods.iteritems()):
            field = getattr(cls, field_name)
            for other in others:
                other_field = getattr(cls, other)
                setattr(field, attribute,
                    getattr(field, attribute)
                    | getattr(other_field, attribute))

        # Set name to fields
        for name, field in cls._fields.iteritems():
            if field.name is None:
                field.name = name
            else:
                assert field.name == name, (
                    'Duplicate fields on %s: %s, %s'
                    % (cls, field.name, name))

    @classmethod
    def _get_name(cls):
        '''
        Returns the first non-empty line of the model docstring.
        '''
        lines = cls.__doc__.splitlines()
        for line in lines:
            line = line.strip()
            if line:
                return line

    @classmethod
    def __register__(cls, module_name):
        """
        Add model in ir.model and ir.model.field.
        """
        super(Model, cls).__register__(module_name)
        pool = Pool()
        Translation = pool.get('ir.translation')
        Model_ = pool.get('ir.model')
        ModelField = pool.get('ir.model.field')

        model_id = Model_.register(cls, module_name)
        ModelField.register(cls, module_name, model_id)

        Translation.register_model(cls, module_name)
        Translation.register_fields(cls, module_name)
        Translation.register_error_messages(cls, module_name)

    @classmethod
    def default_get(cls, fields_names, with_rec_name=True,
            with_on_change=True):
        '''
        Return a dict with the default values for each field in fields_names.
        If with_rec_name is True, rec_name will be added.
        If with_on_change is True, on_change will be added.
        '''
        pool = Pool()
        Property = pool.get('ir.property')
        value = {}

        # get the default values defined in the object
        for field_name in fields_names:
            if field_name in cls._defaults:
                value[field_name] = cls._defaults[field_name]()
            field = cls._fields[field_name]
            if (field._type == 'boolean'
                    and not field_name in value):
                value[field_name] = False
            if isinstance(field, fields.Property):
                value[field_name] = Property.get(field_name, cls.__name__)
            if (with_rec_name
                    and field._type in ('many2one',)
                    and value.get(field_name)):
                Target = pool.get(field.model_name)
                if 'rec_name' in Target._fields:
                    value[field_name + '.rec_name'] = Target(
                        value[field_name]).rec_name

        if with_on_change:
            value = cls._default_on_change(value)
        if not with_rec_name:
            for field in value.keys():
                if field.endswith('.rec_name'):
                    del value[field]
        return value

    @classmethod
    def _default_on_change(cls, value):
        """
        Call on_change function for the default value
        and return new default value
        """
        pool = Pool()
        res = value.copy()
        val = {}
        for field in value.keys():
            if field in cls._fields:
                if cls._fields[field].on_change:
                    inst = cls()
                    for fname in cls._fields[field].on_change:
                        setattr(inst, fname, value.get(fname))
                    val.update(getattr(inst, 'on_change_' + field)())
                if cls._fields[field]._type in ('one2many',):
                    Target = pool.get(cls._fields[field].model_name)
                    for val2 in res[field]:
                        val2.update(Target._default_on_change(val2))
        res.update(val)
        return res

    @classmethod
    def fields_get(cls, fields_names=None):
        """
        Return the definition of each field on the model.
        """
        res = {}
        pool = Pool()
        Translation = pool.get('ir.translation')
        FieldAccess = pool.get('ir.model.field.access')
        ModelAccess = pool.get('ir.model.access')

        #Add translation to cache
        language = Transaction().language
        trans_args = []
        for field in (x for x in cls._fields.keys()
                if ((not fields_names) or x in fields_names)):
            trans_args.append((cls.__name__ + ',' + field, 'field', language,
                None))
            trans_args.append((cls.__name__ + ',' + field, 'help', language,
                None))
            if hasattr(cls._fields[field], 'selection'):
                if (isinstance(cls._fields[field].selection, (tuple, list))
                        and ((hasattr(cls._fields[field],
                                    'translate_selection')
                                and cls._fields[field].translate_selection)
                            or not hasattr(cls._fields[field],
                                'translate_selection'))):
                    sel = cls._fields[field].selection
                    for (key, val) in sel:
                        trans_args.append((cls.__name__ + ',' + field,
                            'selection', language, val))
        Translation.get_sources(trans_args)

        encoder = PYSONEncoder()

        accesses = FieldAccess.get_access([cls.__name__])[cls.__name__]
        for field in (x for x in cls._fields.keys()
                if ((not fields_names) or x in fields_names)):
            res[field] = {
                'type': cls._fields[field]._type,
                'name': field,
                }
            for arg in (
                    'string',
                    'readonly',
                    'states',
                    'size',
                    'required',
                    'translate',
                    'help',
                    'select',
                    'on_change',
                    'add_remove',
                    'on_change_with',
                    'autocomplete',
                    'sort',
                    'datetime_field',
                    'loading',
                    'filename',
                    'selection_change_with',
                    'domain',
                    ):
                if getattr(cls._fields[field], arg, None) is not None:
                    value = getattr(cls._fields[field], arg)
                    if isinstance(value, set):
                        value = list(value)
                    else:
                        value = copy.copy(value)
                    res[field][arg] = value
            if not accesses.get(field, {}).get('write', True):
                res[field]['readonly'] = True
                if res[field].get('states') and \
                        'readonly' in res[field]['states']:
                    del res[field]['states']['readonly']
            for arg in ('digits', 'invisible'):
                if hasattr(cls._fields[field], arg) \
                        and getattr(cls._fields[field], arg):
                    res[field][arg] = copy.copy(getattr(cls._fields[field],
                        arg))
            if (isinstance(cls._fields[field],
                        (fields.Function, fields.One2Many))
                    and not getattr(cls, 'order_%s' % field, None)):
                res[field]['sortable'] = False
            if ((isinstance(cls._fields[field], fields.Function)
                    and not cls._fields[field].searcher)
                    or cls._fields[field]._type in ('binary', 'sha')):
                res[field]['searchable'] = False
            else:
                res[field]['searchable'] = True

            if Transaction().context.get('language'):
                # translate the field label
                res_trans = Translation.get_source(
                    cls.__name__ + ',' + field, 'field',
                    Transaction().context['language'])
                if res_trans:
                    res[field]['string'] = res_trans
                help_trans = Translation.get_source(
                    cls.__name__ + ',' + field, 'help',
                    Transaction().context['language'])
                if help_trans:
                    res[field]['help'] = help_trans

            if hasattr(cls._fields[field], 'selection'):
                if isinstance(cls._fields[field].selection, (tuple, list)):
                    sel = copy.copy(cls._fields[field].selection)
                    if (Transaction().context.get('language')
                            and ((hasattr(cls._fields[field],
                                        'translate_selection')
                                    and cls._fields[field].translate_selection)
                                or not hasattr(cls._fields[field],
                                    'translate_selection'))):
                        # translate each selection option
                        sel2 = []
                        for (key, val) in sel:
                            val2 = Translation.get_source(
                                cls.__name__ + ',' + field, 'selection',
                                language, val)
                            sel2.append((key, val2 or val))
                        sel = sel2
                    res[field]['selection'] = sel
                else:
                    # call the 'dynamic selection' function
                    res[field]['selection'] = copy.copy(
                            cls._fields[field].selection)
            if res[field]['type'] in (
                    'one2many',
                    'many2many',
                    'many2one',
                    'one2one',
                    ):
                if hasattr(cls._fields[field], 'model_name'):
                    relation = copy.copy(cls._fields[field].model_name)
                else:
                    relation = copy.copy(
                        cls._fields[field].get_target().__name__)
                res[field]['relation'] = relation
                res[field]['context'] = copy.copy(cls._fields[field].context)
                res[field]['create'] = accesses.get(field, {}).get('create',
                    True)
                res[field]['delete'] = accesses.get(field, {}).get('delete',
                    True)
            if res[field]['type'] == 'one2many' \
                    and getattr(cls._fields[field], 'field', None):
                res[field]['relation_field'] = copy.copy(
                        cls._fields[field].field)
            if res[field]['type'] == 'many2one':
                target = cls._fields[field].get_target()
                for target_name, target_field in target._fields.iteritems():
                    if (target_field._type == 'one2many'
                            and target_field.model_name == cls.__name__
                            and target_field.field == field):
                        res[field]['relation_field'] = target_name
                        break
            if res[field]['type'] in ('datetime', 'time'):
                res[field]['format'] = copy.copy(cls._fields[field].format)
            if res[field]['type'] == 'selection':
                res[field]['context'] = copy.copy(cls._fields[field].context)
            if res[field]['type'] == 'dict':
                res[field]['schema_model'] = cls._fields[field].schema_model
                res[field]['domain'] = copy.copy(cls._fields[field].domain)
                res[field]['context'] = copy.copy(cls._fields[field].context)
                res[field]['create'] = accesses.get(field, {}).get('create',
                    True)
                res[field]['delete'] = accesses.get(field, {}).get('delete',
                    True)

            # convert attributes into pyson
            for attr in ('states', 'domain', 'context', 'digits', 'size',
                    'add_remove', 'format'):
                if attr in res[field]:
                    res[field][attr] = encoder.encode(res[field][attr])

        for i in res.keys():
            # filter out fields which aren't in the fields_names list
            if fields_names:
                if i not in fields_names:
                    del res[i]
            elif not ModelAccess.check_relation(cls.__name__, i, mode='read'):
                del res[i]
        return res

    def on_change_with(self, fieldnames):
        changes = {}
        for fieldname in fieldnames:
            method_name = 'on_change_with_%s' % fieldname
            changes[fieldname] = getattr(self, method_name)()
        return changes

    def pre_validate(self):
        pass

    def __init__(self, id=None, **kwargs):
        super(Model, self).__init__()
        if id is not None:
            id = int(id)
        self.__dict__['id'] = id
        self._values = None
        parent_values = {}
        for name, value in kwargs.iteritems():
            if not name.startswith('_parent_'):
                setattr(self, name, value)
            else:
                parent_values[name] = value
        for name, value in parent_values.iteritems():
            parent_name, field = name.split('.', 1)
            parent_name = parent_name[8:]  # Strip '_parent_'
            parent = getattr(self, parent_name, None)
            if parent is not None:
                setattr(parent, field, value)
            else:
                setattr(self, parent_name, {field: value})

    def __getattr__(self, name):
        if name == 'id':
            return self.__dict__['id']
        elif self._values and name in self._values:
            return self._values.get(name)
        raise AttributeError("'%s' Model has no attribute '%s': %s"
            % (self.__name__, name, self._values))

    def __setattr__(self, name, value):
        if name == 'id':
            self.__dict__['id'] = value
            return
        super(Model, self).__setattr__(name, value)

    def __getitem__(self, name):
        warnings.warn('Use __getattr__ instead of __getitem__',
            DeprecationWarning, stacklevel=2)
        return getattr(self, name)

    def __contains__(self, name):
        return name in self._fields

    def __int__(self):
        return int(self.id)

    def __str__(self):
        return '%s,%s' % (self.__name__, self.id)

    def __unicode__(self):
        return u'%s,%s' % (self.__name__, self.id)

    def __repr__(self):
        if self.id < 0:
            return "Pool().get('%s')(**%s)" % (self.__name__,
                repr(self._default_values))
        else:
            return "Pool().get('%s')(%s)" % (self.__name__, self.id)

    def __eq__(self, other):
        if not isinstance(other, Model):
            return NotImplemented
        if self.id is None or other.id is None:
            return False
        return (self.__name__, self.id) == (other.__name__, other.id)

    def __lt__(self, other):
        if not isinstance(other, Model) or self.__name__ != other.__name__:
            return NotImplemented
        return self.id < other.id

    # TODO: replace by total_ordering when 2.6 will be dropped
    __gt__ = lambda self, other: not (self < other or self == other)
    __le__ = lambda self, other: self < other or self == other
    __ge__ = lambda self, other: not self < other

    def __ne__(self, other):
        if not isinstance(other, Model):
            return NotImplemented
        if self.id is None or other.id is None:
            return True
        return (self.__name__, self.id) != (other.__name__, other.id)

    def __hash__(self):
        return hash((self.__name__, self.id))

    def __nonzero__(self):
        return True

    @property
    def _default_values(self):
        if self.id >= 0:
            return self.id
        values = {}
        if self._values:
            for fname, value in self._values.iteritems():
                field = self._fields[fname]
                if isinstance(field, fields.Reference):
                    if value is not None:
                        value = str(value)
                elif isinstance(value, Model):
                    value = value._default_values
                elif isinstance(value, list):
                    value = [r._default_values for r in value]
                values[fname] = value
        return values
