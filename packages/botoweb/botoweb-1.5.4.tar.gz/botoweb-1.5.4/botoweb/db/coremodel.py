# Copyright (c) 2006,2007,2008 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from botoweb.db.manager import get_manager
from botoweb.db.property import Property, JSON
from botoweb.db.key import Key
from botoweb.db.query import Query
from decimal import Decimal
from datetime import datetime, date
import time
import logging
log = logging.getLogger('botoweb.db.model')


class ModelMeta(type):
	'''Metaclass for all Models'''

	def __init__(cls, name, bases, dict):
		super(ModelMeta, cls).__init__(name, bases, dict)
		# Make sure this is a subclass of Model - mainly copied from django ModelBase (thanks!)
		cls.__sub_classes__ = []
		try:
			if filter(lambda b: issubclass(b, Model), bases):
				for base in bases:
					base.__sub_classes__.append(cls)
				cls._manager = get_manager(cls)
				# look for all of the Properties and set their names
				for key in dict.keys():
					if isinstance(dict[key], Property):
						property = dict[key]
						property.__property_config__(cls, key)
				prop_names = []
				props = cls.properties()
				for prop in props:
					if not prop.__class__.__name__.startswith('_'):
						prop_names.append(prop.name)
				setattr(cls, '_prop_names', prop_names)
		except NameError:
			# 'Model' isn't defined yet, meaning we're looking at our own
			# Model class, defined below.
			pass


class Model(object):
	__metaclass__ = ModelMeta
	__consistent__ = False  # Consistent is set off by default
	_raw_item = None  # Allows us to cache the raw items
	id = None

	@classmethod
	def get_lineage(cls):
		l = [c.__name__ for c in cls.mro()]
		l.reverse()
		return '.'.join(l)

	@classmethod
	def kind(cls):
		return cls.__name__

	@classmethod
	def _get_by_id(cls, id, manager=None):
		if not manager:
			manager = cls._manager
		return manager.get_object(cls, id)

	@classmethod
	def lookup(cls, *args, **kwargs):
		'''
			returns get_by_id function value from the class that called lookup.
		'''
		return cls.get_by_id(*args, **kwargs)

	@classmethod
	def get_by_id(cls, ids=None, parent=None):
		if isinstance(ids, list):
			objs = [cls._get_by_id(id) for id in ids]
			return objs
		else:
			return cls._get_by_id(ids)

	get_by_ids = get_by_id

	@classmethod
	def get_by_key_name(cls, key_names, parent=None):
		raise NotImplementedError('Key Names are not currently supported')

	@classmethod
	def find(cls, limit=None, next_token=None, **params):
		q = Query(cls, limit=limit, next_token=next_token)
		for key, value in params.items():
			q.filter('%s =' % key, value)
		return q

	@classmethod
	def match_reference_property(cls, reference_property, model_instance):
		'''
		:param reference_property: Name (or list of names) of the reference property to match
		:type reference_property: str or list
		:param model_instance: Model instance to match to reference property
		:type model_instance: :class:`~.Model`
		:return: An iterator with the matched instances of this class
		:rtype: :class:`~botoweb.db.query.Query`
		'''
		query = Query(cls)
		if isinstance(reference_property, basestring):
			return query.filter(reference_property + ' =', model_instance)
		else:
			props = ['%s =' % prop for prop in reference_property]
			return query.filter(props, model_instance)

	@classmethod
	def all(cls, limit=None, next_token=None):
		return cls.find(limit=limit, next_token=next_token)

	@classmethod
	def get_or_insert(key_name, **kw):
		raise NotImplementedError('get_or_insert not currently supported')

	@classmethod
	def properties(cls, hidden=True):
		properties = []
		while cls:
			for key in cls.__dict__.keys():
				prop = cls.__dict__[key]
				if isinstance(prop, Property):
					if hidden or not prop.__class__.__name__.startswith('_'):
						properties.append(prop)
			if len(cls.__bases__) > 0:
				cls = cls.__bases__[0]
			else:
				cls = None
		return properties

	@classmethod
	def find_property(cls, prop_name):
		property = None
		while cls:
			for key in cls.__dict__.keys():
				prop = cls.__dict__[key]
				if isinstance(prop, Property):
					if not prop.__class__.__name__.startswith('_') and prop_name == prop.name:
						property = prop
			if len(cls.__bases__) > 0:
				cls = cls.__bases__[0]
			else:
				cls = None
		return property

	@classmethod
	def get_xmlmanager(cls):
		if not hasattr(cls, '_xmlmanager'):
			from botoweb.db.manager.xmlmanager import XMLManager
			cls._xmlmanager = XMLManager(cls, None, None, None,
											None, None, None, None, False)
		return cls._xmlmanager

	@classmethod
	def from_xml(cls, fp):
		xmlmanager = cls.get_xmlmanager()
		return xmlmanager.unmarshal_object(fp)

	def __init__(self, id=None, **kw):
		self._loaded = False
		self._validate = False
		# first try to initialize all properties to their default values
		for prop in self.properties(hidden=False):
			try:
				setattr(self, prop.name, prop.default_value())
			except ValueError:
				pass
		if 'manager' in kw:
			self._manager = kw['manager']
		self.id = id
		for key in kw:
			if key != 'manager':
				# We don't want any errors populating up when loading an object,
				# so if it fails we just revert to it's default value
				try:
					setattr(self, key, kw[key])
				except Exception, e:
					log.exception(e)
		self._validate = True

	def __repr__(self):
		return '%s<%s>' % (self.__class__.__name__, self.id)

	def __str__(self):
		return str(self.id)

	def __eq__(self, other):
		return other and isinstance(other, Model) and self.id == other.id

	def _get_raw_item(self):
		if not self._raw_item:
			self._raw_item = self._manager.get_raw_item(self)
		return self._raw_item

	def load(self):
		if self.id and not self._loaded:
			self._manager.load_object(self)

	def reload(self):
		if self.id:
			self._loaded = False
			self._manager.load_object(self)

	def put(self, expected_value=None):
		'''
		Save this object as it is, with an optional expected value

		:param expected_value: Optional tuple of Attribute, and Value that
			must be the same in order to save this object. If this
			condition is not met, an SDBResponseError will be raised with a
			Confict status code.
		:type expected_value: tuple or list
		:return: This object
		:rtype: :class:`~.Model`
		'''
		self._manager.save_object(self, expected_value)
		return self

	save = put

	def put_attributes(self, attrs):
		'''
		Save just these few attributes, not the whole object

		:param attrs: Attributes to save, key->value dict
		:type attrs: dict
		:return: self
		:rtype: :class:`~.Model`
		'''
		assert(isinstance(attrs, dict)), 'Argument must be a dict of key->values to save'
		for prop_name in attrs:
			value = attrs[prop_name]
			prop = self.find_property(prop_name)
			assert(prop), 'Property not found: %s' % prop_name
			self._manager.set_property(prop, self, prop_name, value)
		self.reload()
		return self

	def delete_attributes(self, attrs):
		'''
		Delete just these attributes, not the whole object.

		:param attrs: Attributes to save, as a list of string names
		:type attrs: list
		:return: self
		:rtype: :class:`~.Model`
		'''
		assert(isinstance(attrs, list)), 'Argument must be a list of names of keys to delete.'
		self._manager.domain.delete_attributes(self.id, attrs)
		self.reload()
		return self

	save_attributes = put_attributes

	def delete(self):
		self._manager.delete_object(self)

	def key(self):
		return Key(obj=self)

	def set_manager(self, manager):
		self._manager = manager

	# Conversion to and from dictionary objects, for simple
	# serialization with the JSON module

	def to_dict(self, recursive=False):
		'''Get this generic object as simple DICT
		that can be easily JSON encoded'''
		from botoweb.db.query import Query
		from botoweb.db.property import CalculatedProperty, IntegerProperty, _ReverseReferenceProperty
		ret = {'__type__': self.__class__.__name__, '__id__': self.id}
		for prop_type in self.properties():
			prop_name = prop_type.name
			# Don't mess with calculated properties
			if isinstance(prop_type, CalculatedProperty) or isinstance(prop_type, _ReverseReferenceProperty):
				continue
			val = getattr(self, prop_name)
			if val is None:
				pass
			elif isinstance(val, int) or isinstance(val, long):
				val = val
			elif isinstance(val, basestring) and isinstance(prop_type, IntegerProperty):
				# Handle strings masquarading as integers
				if val:
					try:
						val = int(val)
					except:
						log.exception('Could not convert value to integer', val)
				else:
					val = 0
			elif isinstance(val, Model):
				val = val.id
			elif isinstance(val, datetime) or isinstance(val, date):
				# Convert the datetime to a timestamp
				val = int(time.mktime((val.year, val.month, val.day,
						val.hour, val.minute, val.second,
						-1, -1, -1)))
			elif hasattr(val, 'isoformat'):
				val = val.isoformat() + 'Z'
			elif isinstance(val, Query):
				if recursive:
					val = [v.to_dict() for v in val]
				else:
					# If we're not recursive, we ignore queries
					continue
			elif isinstance(val, list):
				rv = []
				for v in val:
					if v is not None:
						if isinstance(v, unicode):
							v = v.encode('utf-8')
						else:
							v = str(v)
						rv.append(v)
				val = rv
			elif isinstance(val, dict):
				rv = {}
				for k in val:
					if val[k] is not None:
						if isinstance(val[k], unicode):
							rv[k] = val[k].encode('utf-8')
						else:
							rv[k] = str(val[k])
				val = rv
			elif isinstance(val, JSON):
				val = val.value
			else:
				# Fall back to encoding as a string
				try:
					val = str(val)
				except:
					val = unicode(val)
			ret[prop_name] = val
		return ret

	@classmethod
	def from_dict(cls, data):
		'''Load this object from a dictionary as exported by
		to_dict'''
		obj = cls(data['__id__'])
		obj._loaded = True
		obj._validate = False
		for prop_name in data:
			val = data[prop_name]
			if prop_name == '__id__':
				obj.id = val
			elif not prop_name.startswith('_'):
				prop = obj.find_property(prop_name)
				if prop:
					if hasattr(prop, 'reference_class'):
						t = prop.reference_class
					else:
						t = prop.data_type
					val = cls._decode(t, val, prop)
					setattr(obj, prop_name, val)
		obj._validate = True
		return obj

	@classmethod
	def _decode(cls, t, val, prop):
		if val is None:
			return val
		if isinstance(val, dict) and '__id__' in val:
			val = t(val['__id__'])
		elif isinstance(val, dict) and 'ID' in val:
			val = t(val['ID'])
		elif t == datetime:
			# Some exports turn this into an integer,
			# which is the Unix Timestamp
			if isinstance(val, int) or isinstance(val, Decimal):
				val = datetime.fromtimestamp(val)
			elif 'T' in val:
				# If there a "T" in the datetime value, then
				# it's a full date and time

				# Remove fractional seconds, Z or +00:00Z time zone formatting
				# Times are in UTC so formatting inconsistencies can be ignored
				val = val[:19]
				val = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
			else:
				# Otherwise, it may just be a date
				val = val.split('-')
				try:
					val = date(int(val[0]), int(val[1]), int(val[2]))
				except:
					return None
		elif t == list:
			if not isinstance(val, list) and not isinstance(val, set):
				val = [val]
			val = [cls._decode(prop.item_type, v, prop) for v in val]
		elif t not in (str, unicode, int):
			val = t(val)
		return val

	def to_xml(self, doc=None):
		xmlmanager = self.get_xmlmanager()
		doc = xmlmanager.marshal_object(self, doc)
		return doc

	@classmethod
	def find_subclass(cls, name):
		'''Find a subclass with a given name'''
		if name == cls.__name__:
			return cls
		for sc in cls.__sub_classes__:
			r = sc.find_subclass(name)
			if r is not None:
				return r


class Expando(Model):

	def __setattr__(self, name, value):
		if name in self._prop_names:
			object.__setattr__(self, name, value)
		elif name.startswith('_'):
			object.__setattr__(self, name, value)
		elif name == 'id':
			object.__setattr__(self, name, value)
		else:
			self._manager.set_key_value(self, name, value)
			object.__setattr__(self, name, value)

	def __getattr__(self, name):
		if not name.startswith('_'):
			value = self._manager.get_key_value(self, name)
			if value:
				object.__setattr__(self, name, value)
				return value
		raise AttributeError
