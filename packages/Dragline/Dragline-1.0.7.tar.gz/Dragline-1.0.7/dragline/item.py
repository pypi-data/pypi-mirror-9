from pprint import pformat
from collections import MutableMapping
from abc import ABCMeta
import six
from datetime import datetime
import json


class BaseItem(object):
    """Base class for all scraped items."""
    pass


class Field(object):
    primary = False
    """Container of field metadata"""
    def __init__(self, **args):
        for k, v in args.items():
            setattr(self, k, v)

    def validate(self, value):
        return value

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class TextField(Field):
    type = 'text'

    def validate(self, value):
        if not isinstance(value, basestring):
            raise TypeError('got value of {} expected {}'.format(type(value), 'basestring'))
        return value


class IntField(Field):
    type = 'int'

    def validate(self, value):
        try:
            value = int(value)
        except:
            raise TypeError('got value of {} expected {}'.format(type(value), self.type))
        return value


class DecimalField(Field):
    type = 'double'

    def validate(self, value):
        try:
            value = float(value)
        except:
            raise TypeError('got value of {} expected {}'.format(type(value), 'float'))
        return value


class JSONField(Field):
    type = 'text'

    def validate(self, value):
        if isinstance(value, basestring):
            try:
                json.loads(value)
            except:
                value = json.dumps(value)
        else:
            try:
                value = json.dumps(value)
            except:
                raise TypeError('unable to json serialize, {}'.format(value))
        return "json(" + value + ')'


class DatetimeField(Field):
    type = 'timestamp'

    def validate(self, value):
        if not isinstance(value, datetime):
            raise TypeError('got value of {} expected {}'.format(type(value), 'datetime'))
        return value


class ItemMeta(ABCMeta):

    def __new__(mcs, class_name, bases, attrs):
        fields = {}
        new_attrs = {}
        for n, v in six.iteritems(attrs):
            if isinstance(v, Field):
                fields[n] = v
            else:
                new_attrs[n] = v

        cls = super(ItemMeta, mcs).__new__(mcs, class_name, bases, new_attrs)
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        return cls


class DictItem(MutableMapping, BaseItem):

    fields = {}

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in six.iteritems(dict(*args, **kwargs)):
                self[k] = v

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self.fields:
            if value is None:
                self._values[key] = None
            else:
                self._values[key] = self.fields[key].validate(value)
        else:
            raise KeyError("%s does not support field: %s" %
                (self.__class__.__name__, key))

    def __delitem__(self, key):
        del self._values[key]

    def __getattr__(self, name):
        if name in self.fields:
            raise AttributeError("Use item[%r] to get field value" % name)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            raise AttributeError("Use item[%r] = %r to set field value" % (name, value))
        super(DictItem, self).__setattr__(name, value)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    __hash__ = BaseItem.__hash__

    def keys(self):
        return self._values.keys()

    def __repr__(self):
        return pformat(dict(self))

    def copy(self):
        return self.__class__(self)


@six.add_metaclass(ItemMeta)
class Item(DictItem):
    def save(self, *args, **kwargs):
        print dict(self)

