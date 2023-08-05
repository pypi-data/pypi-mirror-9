# Copyright (c) 2006,2007,2008 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2014 Saikat DebRoy
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

import datetime
from botoweb.db.key import Key
from boto.utils import Password
from botoweb.db.query import Query
import re
import boto
import boto.s3.key
from botoweb.db.blob import Blob
import logging
log = logging.getLogger('newscore')


class Property(object):

	data_type = str
	type_name = ''
	name = ''
	verbose_name = ''
	is_calculated = False

	def __init__(self, verbose_name=None, name=None, default=None, required=False,
				validator=None, choices=None, unique=False):
		self.verbose_name = verbose_name
		self.name = name
		self.default = default
		self.required = required
		self.validator = validator
		self.choices = choices
		if self.name:
			self.slot_name = '_' + self.name
		else:
			self.slot_name = '_'
		self.unique = unique

	def __get__(self, obj, objtype):
		#log.info('%s,%s' % (self.slot_name,objtype))
		#log.info(self.verbose_name)
		if obj:
			obj.load()
			return getattr(obj, self.slot_name)
		else:
			return None

	def __set__(self, obj, value):
		if obj._validate is not False:
			self.validate(value)

		# Fire off any on_set functions
		try:
			if obj._loaded and hasattr(obj, 'on_set_%s' % self.name):
				fnc = getattr(obj, 'on_set_%s' % self.name)
				value = fnc(value)
		except Exception:
			boto.log.exception('Exception running on_set_%s' % self.name)

		setattr(obj, self.slot_name, value)

	def __property_config__(self, model_class, property_name):
		self.model_class = model_class
		self.name = property_name
		self.slot_name = '_' + self.name

	def default_validator(self, value):
		if isinstance(value, basestring) or value == self.default_value():
			return
		if not isinstance(value, self.data_type):
			raise TypeError('Validation Error, %s.%s expecting %s, got %s' % (self.model_class.__name__, self.name, self.data_type, type(value)))

	def default_value(self):
		return self.default

	def validate(self, value):
		if self.required and value is None:
			raise ValueError('%s is a required property' % self.name)
		if self.choices and value and not value in self.choices:
			raise ValueError('%s not a valid choice for %s.%s' % (value, self.model_class.__name__, self.name))
		if self.validator:
			self.validator(value)
		else:
			self.default_validator(value)
		return value

	def empty(self, value):
		return not value

	def get_value_for_datastore(self, model_instance):
		return getattr(model_instance, self.name)

	def make_value_from_datastore(self, value):
		return value

	def get_choices(self):
		if callable(self.choices):
			return self.choices()
		return self.choices


def validate_string(value):
	if value is None:
		return
	elif isinstance(value, str) or isinstance(value, unicode):
		if len(value) > 1024:
			raise ValueError('Length of value greater than maxlength')
	else:
		raise TypeError('Expecting String, got %s' % type(value))


class StringProperty(Property):

	type_name = 'String'

	def __init__(self, verbose_name=None, name=None, default='', required=False,
				validator=validate_string, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)


class TextProperty(Property):

	type_name = 'Text'

	def __init__(self, verbose_name=None, name=None, default='', required=False,
				validator=None, choices=None, unique=False, max_length=None):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)
		self.max_length = max_length

	def validate(self, value):
		value = super(TextProperty, self).validate(value)
		if not isinstance(value, str) and not isinstance(value, unicode):
			raise TypeError('Expecting Text, got %s' % type(value))
		if self.max_length and len(value) > self.max_length:
			raise ValueError('Length of value greater than maxlength %s' % self.max_length)


class PasswordProperty(StringProperty):
	'''

	Hashed property whose original value can not be
	retrieved, but still can be compared.

	Works by storing a hash of the original value instead
	of the original value.  Once that's done all that
	can be retrieved is the hash.

	The comparison

	   obj.password == 'foo'

	generates a hash of 'foo' and compares it to the
	stored hash.

	Underlying data type for hashing, storing, and comparing
	is boto.utils.Password.  The default hash function is
	defined there ( currently sha512 in most cases, md5
	where sha512 is not available )

	It's unlikely you'll ever need to use a different hash
	function, but if you do, you can control the behavior
	in one of two ways:

	  1) Specifying hashfunc in PasswordProperty constructor

		 import hashlib

		 class MyModel(model):
			 password = PasswordProperty(hashfunc=hashlib.sha224)

	  2) Subclassing Password and PasswordProperty

		 class SHA224Password(Password):
			 hashfunc=hashlib.sha224

		 class SHA224PasswordProperty(PasswordProperty):
			 data_type=MyPassword
			 type_name='MyPassword'

		 class MyModel(Model):
			 password = SHA224PasswordProperty()

	'''
	data_type = Password
	type_name = 'Password'

	def __init__(self, verbose_name=None, name=None, default='', required=False,
				validator=None, choices=None, unique=False, hashfunc=None):

		'''
		   The hashfunc parameter overrides the default hashfunc in boto.utils.Password.

		   The remaining parameters are passed through to StringProperty.__init__'''

		StringProperty.__init__(self, verbose_name, name, default, required, validator, choices, unique)
		self.hashfunc = hashfunc

	def make_value_from_datastore(self, value):
		p = self.data_type(value, hashfunc=self.hashfunc)
		return p

	def get_value_for_datastore(self, model_instance):
		value = StringProperty.get_value_for_datastore(self, model_instance)
		if value and len(value):
			return str(value)
		else:
			return None

	def __set__(self, obj, value):
		if not isinstance(value, self.data_type):
			p = self.data_type(hashfunc=self.hashfunc)
			p.set(value)
			value = p
		Property.__set__(self, obj, value)

	def __get__(self, obj, objtype):
		return self.data_type(StringProperty.__get__(self, obj, objtype), hashfunc=self.hashfunc)

	def validate(self, value):
		value = Property.validate(self, value)
		if isinstance(value, self.data_type):
			if len(value) > 1024:
				raise ValueError('Length of value greater than maxlength')
		else:
			raise TypeError('Expecting %s, got %s' % (type(self.data_type), type(value)))


class BlobProperty(Property):
	data_type = Blob
	type_name = 'blob'

	def __set__(self, obj, value):
		if value != self.default_value():
			if not isinstance(value, Blob):
				oldb = self.__get__(obj, type(obj))
				id = None
				if oldb:
					id = oldb.id
				b = Blob(value=value, id=id)
				value = b
		Property.__set__(self, obj, value)


class S3KeyProperty(Property):

	data_type = boto.s3.key.Key
	type_name = 'S3Key'
	validate_regex = '^s3:\/\/([^\/]*)\/(.*)$'

	def __init__(self, verbose_name=None, name=None, default=None,
				required=False, validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required,
							validator, choices, unique)

	def validate(self, value):
		value = super(S3KeyProperty, self).validate(value)
		if value == self.default_value() or value == str(self.default_value()):
			return self.default_value()
		if isinstance(value, self.data_type):
			return
		match = re.match(self.validate_regex, value)
		if match:
			return
		raise TypeError('Validation Error, expecting %s, got %s' % (self.data_type, type(value)))

	def __get__(self, obj, objtype):
		value = Property.__get__(self, obj, objtype)
		if value:
			if isinstance(value, self.data_type):
				return value
			match = re.match(self.validate_regex, value)
			if match:
				s3 = obj._manager.get_s3_connection()
				bucket = s3.get_bucket(match.group(1), validate=False)
				k = bucket.get_key(match.group(2))
				if not k:
					k = bucket.new_key(match.group(2))
					k.set_contents_from_string('')
				return k
		else:
			return value

	def get_value_for_datastore(self, model_instance):
		value = Property.get_value_for_datastore(self, model_instance)
		if value:
			return 's3://%s/%s' % (value.bucket.name, value.name)
		else:
			return None


class IntegerProperty(Property):

	data_type = int
	type_name = 'Integer'

	def __init__(self, verbose_name=None, name=None, default=0, required=False,
				validator=None, choices=None, unique=False, max=2147483647, min=-2147483648):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)
		self.max = max
		self.min = min

	def validate(self, value):
		value = int(value)
		value = Property.validate(self, value)
		if value > self.max:
			raise ValueError('Maximum value is %d' % self.max)
		if value < self.min:
			raise ValueError('Minimum value is %d' % self.min)
		return value

	def empty(self, value):
		return value is None

	def __set__(self, obj, value):
		if value == '' or value is None:
			value = 0
		return Property.__set__(self, obj, value)


class LongProperty(Property):

	data_type = long
	type_name = 'Long'

	def __init__(self, verbose_name=None, name=None, default=0, required=False,
				validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)

	def validate(self, value):
		value = long(value)
		value = Property.validate(self, value)
		min = -9223372036854775808
		max = 9223372036854775807
		if value > max:
			raise ValueError('Maximum value is %d' % max)
		if value < min:
			raise ValueError('Minimum value is %d' % min)
		return value

	def empty(self, value):
		return value is None

class BooleanProperty(Property):

	data_type = bool
	type_name = 'Boolean'

	def __init__(self, verbose_name=None, name=None, default=False, required=False,
				validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)

	def empty(self, value):
		return value is None

class FloatProperty(Property):

	data_type = float
	type_name = 'Float'

	def __init__(self, verbose_name=None, name=None, default=0.0, required=False,
				validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)

	def validate(self, value):
		value = float(value)
		value = Property.validate(self, value)
		return value

	def empty(self, value):
		return value is None

class DateTimeProperty(Property):
	'''This class handles both the datetime.datetime object
	And the datetime.date objects. It can return either one,
	depending on the value stored in the database'''

	data_type = datetime.datetime
	type_name = 'DateTime'

	def __init__(self, verbose_name=None, auto_now=False, auto_now_add=False, name=None,
				default=None, required=False, validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)
		self.auto_now = auto_now
		self.auto_now_add = auto_now_add

	def default_value(self):
		if self.auto_now or self.auto_now_add:
			return self.now()
		return Property.default_value(self)

	def validate(self, value):
		if value is None:
			return
		if isinstance(value, datetime.date):
			return value
		return super(DateTimeProperty, self).validate(value)

	def get_value_for_datastore(self, model_instance):
		if self.auto_now:
			setattr(model_instance, self.name, self.now())
		return Property.get_value_for_datastore(self, model_instance)

	def now(self):
		return datetime.datetime.utcnow()

class DateProperty(Property):

	data_type = datetime.date
	type_name = 'Date'

	def __init__(self, verbose_name=None, auto_now=False, auto_now_add=False, name=None,
				default=None, required=False, validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)
		self.auto_now = auto_now
		self.auto_now_add = auto_now_add

	def default_value(self):
		if self.auto_now or self.auto_now_add:
			return self.now()
		return Property.default_value(self)

	def validate(self, value):
		value = super(DateProperty, self).validate(value)
		if value is None:
			return
		if not isinstance(value, self.data_type):
			raise TypeError('Validation Error, expecting %s, got %s' % (self.data_type, type(value)))

	def get_value_for_datastore(self, model_instance):
		if self.auto_now:
			setattr(model_instance, self.name, self.now())
		val = Property.get_value_for_datastore(self, model_instance)
		if isinstance(val, datetime.datetime):
			val = val.date()
		return val

	def now(self):
		return datetime.date.today()


class TimeProperty(Property):
	data_type = datetime.time
	type_name = 'Time'

	def __init__(self, verbose_name=None, name=None,
				default=None, required=False, validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)

	def validate(self, value):
		value = super(TimeProperty, self).validate(value)
		if value is None:
			return
		if not isinstance(value, self.data_type):
			raise TypeError('Validation Error, expecting %s, got %s' % (self.data_type, type(value)))


class ReferenceProperty(Property):

	data_type = Key
	type_name = 'Reference'

	def __init__(self, reference_class=None, collection_name=None,
				verbose_name=None, name=None, default=None, required=False, validator=None, choices=None, unique=False):
		Property.__init__(self, verbose_name, name, default, required, validator, choices, unique)
		self.reference_class = reference_class
		self.collection_name = collection_name

	def __get__(self, obj, objtype):
		if obj:
			value = getattr(obj, self.slot_name)
			if value == self.default_value():
				return value
			# If the value is still the UUID for the referenced object, we need to create
			# the object now that is the attribute has actually been accessed.  This lazy
			# instantiation saves unnecessary roundtrips to SimpleDB
			if isinstance(value, str) or isinstance(value, unicode):
				value = self.reference_class(value)
				setattr(obj, self.name, value)
			return value

	def __set__(self, obj, value):
		'''Don't allow this object to be associated to itself
		This causes bad things to happen'''
		if value is not None and (obj.id == value or (hasattr(value, 'id') and obj.id == value.id)):
			raise ValueError('Can not associate an object with itself!')
		return super(ReferenceProperty, self).__set__(obj,value)

	def __property_config__(self, model_class, property_name):
		Property.__property_config__(self, model_class, property_name)
		if self.collection_name is None:
			self.collection_name = '%s_%s_set' % (model_class.__name__.lower(), self.name)
		if hasattr(self.reference_class, self.collection_name):
			raise ValueError('duplicate property: %s' % self.collection_name)
		setattr(self.reference_class, self.collection_name,
				_ReverseReferenceProperty(model_class, property_name, self.collection_name))

	def check_uuid(self, value):
		# This does a bit of hand waving to 'type check' the string
		t = value.split('-')
		if len(t) != 5:
			raise ValueError

	def check_instance(self, value):
		try:
			obj_lineage = value.get_lineage()
			cls_lineage = self.reference_class.get_lineage()
			if obj_lineage.startswith(cls_lineage):
				return
		except:
			raise ValueError('%s is not a Model' % repr(value))
		raise TypeError('%s not instance of %s' % (obj_lineage, cls_lineage))

	def validate(self, value):
		if self.validator:
			self.validator(value)
		if self.required and value==None:
			raise ValueError('%s is a required property' % self.name)
		if value == self.default_value():
			return
		if not isinstance(value, str) and not isinstance(value, unicode):
			self.check_instance(value)

class _ReverseReferenceProperty(Property):
	data_type = Query
	type_name = 'query'

	def __init__(self, model, prop, name):
		self.__model = model
		self.__property = prop
		self.collection_name = prop
		self.name = name
		self.item_type = model

	def __get__(self, model_instance, model_class):
		'''Fetches collection of model instances of this collection property.'''
		if model_instance is not None:
			return self.__model.match_reference_property(self.__property, model_instance)
		else:
			return self

	def __set__(self, model_instance, value):
		'''Not possible to set a new collection.'''
		raise ValueError('Virtual property is read-only')


class CalculatedProperty(Property):
	is_calculated = True

	def __init__(self, verbose_name=None, name=None, default=None,
				required=False, validator=None, choices=None,
				calculated_type=int, unique=False, use_method=False):
		Property.__init__(self, verbose_name, name, default, required,
							validator, choices, unique)
		self.calculated_type = calculated_type
		self.use_method = use_method

	def __get__(self, obj, objtype):
		value = self.default_value()
		if obj:
			try:
				value = getattr(obj, self.slot_name)
				if self.use_method:
					value = value()
			except AttributeError:
				pass
		return value

	def __set__(self, obj, value):
		'''Not possible to set a new AutoID.'''
		pass

	def _set_direct(self, obj, value):
		if not self.use_method:
			setattr(obj, self.slot_name, value)

	def get_value_for_datastore(self, model_instance):
		if self.calculated_type in [str, int, bool]:
			value = self.__get__(model_instance, model_instance.__class__)
			return value
		else:
			return None

class ListProperty(Property):

	data_type = list
	type_name = 'List'

	def __init__(self, item_type, verbose_name=None, name=None, default=None, **kwds):
		if default is None:
			default = []
		self.item_type = item_type
		Property.__init__(self, verbose_name, name, default=default, required=True, **kwds)

	def validate(self, value):
		if self.validator:
			self.validator(value)
		if value is not None:
			if not isinstance(value, list):
				value = [value]

		if self.item_type in (int, long):
			item_type = (int, long)
		elif self.item_type in (str, unicode):
			item_type = (str, unicode)
		else:
			item_type = self.item_type

		for item in value:
			if not isinstance(item, item_type):
				if item_type == (int, long):
					raise ValueError('Items in the %s list must all be integers.' % self.name)
				else:
					raise ValueError('Items in the %s list must all be %s instances, got a %s instead' %
									(self.name, self.item_type.__name__, type(item)))
		return value

	def empty(self, value):
		return value is None

	def default_value(self):
		return list(super(ListProperty, self).default_value())

	def __set__(self, obj, value):
		'''Override the set method to allow them to set the property to an instance of the item_type instead of requiring a list to be passed in'''
		if self.item_type in (int, long):
			item_type = (int, long)
		elif self.item_type in (str, unicode):
			item_type = (str, unicode)
		else:
			item_type = self.item_type
		if isinstance(value, item_type):
			value = [value]
		elif value is None:  # Override to allow them to set this to 'None' to remove everything
			value = []
		return super(ListProperty, self).__set__(obj,value)


class SetProperty(Property):

	data_type = set
	type_name = 'Set'

	def __init__(self, item_type, verbose_name=None, name=None, default=None, **kwds):
		if default is None:
			default = set()
		self.item_type = item_type
		Property.__init__(self, verbose_name, name, default=default, required=True, **kwds)

	def validate(self, value):
		if self.validator:
			self.validator(value)
		if value is not None:
			if not isinstance(value, set):
				value = set(value)

		if self.item_type in (int, long):
			item_type = (int, long)
		elif self.item_type in (str, unicode):
			item_type = (str, unicode)
		else:
			item_type = self.item_type

		for item in value:
			if not isinstance(item, item_type):
				if item_type == (int, long):
					raise ValueError('Items in the %s list must all be integers.' % self.name)
				else:
					raise ValueError('Items in the %s list must all be %s instances, got a %s instead' %
									(self.name, self.item_type.__name__, type(item)))
		return value

	def empty(self, value):
		return value is None

	def default_value(self):
		return set(super(SetProperty, self).default_value())

	def __set__(self, obj, value):
		'''Override the set method to allow them to set the property to an instance of the item_type instead of requiring a list to be passed in'''
		if self.item_type in (int, long):
			item_type = (int, long)
		elif self.item_type in (str, unicode):
			item_type = (str, unicode)
		else:
			item_type = self.item_type
		if isinstance(value, item_type):
			value = set(value)
		elif value is None:  # Override to allow them to set this to 'None' to remove everything
			value = set()
		return super(SetProperty, self).__set__(obj, value)


class MapProperty(Property):

	data_type = dict
	type_name = 'Map'

	def __init__(self, item_type=str, verbose_name=None, name=None, default=None, **kwds):
		if default is None:
			default = {}
		self.item_type = item_type
		Property.__init__(self, verbose_name, name, default=default, required=True, **kwds)

	def validate(self, value):
		value = super(MapProperty, self).validate(value)
		if value is not None:
			if not isinstance(value, dict):
				raise ValueError('Value must of type dict')

		if self.item_type in (int, long):
			item_type = (int, long)
		elif self.item_type in (str, unicode):
			item_type = (str, unicode)
		else:
			item_type = self.item_type

		for key in value:
			if not isinstance(value[key], item_type):
				if item_type == (int, long):
					raise ValueError('Values in the %s Map must all be integers.' % self.name)
				else:
					raise ValueError('Values in the %s Map must all be %s instances' %
									(self.name, self.item_type.__name__))
		return value

	def empty(self, value):
		return value is None

	def default_value(self):
		return {}


class JSON(object):
	def __init__(self, value):
		if isinstance(value, JSON):
			self.value = value.value
		else:
			self.set(value)

	def set(self, value):
		import json
		if isinstance(value, unicode):
			try:
				value = json.loads(value)
			except:
				pass
		try:
			json.dumps(value)
		except Exception as e:
			raise ValueError('%s in %s JSONProperty' % (str(e), self.name))
		self.value = value

	def __eq__(self, other):
		return other is not None and self.value == other.value

	def __ne__(self, other):
		return other is None or self.value != other.value

	def __str__(self):
		return str(self.value)

	def __unicode__(self):
		return unicode(self.value)

	def __len__(self):
		# Note: this fails if self.value is a number
		return len(self.value)

	# Allow this object to be interacted with as a raw object
	def __getattr__(self, name):
		return getattr(self.value, name)

	def __getitem__(self, name):
		return self.value.__getitem__(name)

	def __setitem__(self, name, value):
		return self.value.__setitem__(name, value)

class JSONProperty(Property):

	data_type = JSON
	item_type = JSON
	type_name = 'JSON'

	def __init__(self, verbose_name=None, name=None, default=None, required=False,
				validator=None, choices=None, unique=False):
		default = self.make_value_from_datastore(default)
		super(JSONProperty, self).__init__(verbose_name=verbose_name, name=name,
													  default=default, required=required, validator=validator,
													  choices=choices, unique=unique)

	def make_value_from_datastore(self, value):
		if value is not None:
			value = self.data_type(value)
		return value

	def get_value_for_datastore(self, model_instance):
		value = super(JSONProperty, self).get_value_for_datastore(model_instance)
		if isinstance(value, self.data_type):
			value = value.value
		return value

	def __set__(self, obj, value):
		if not (value is None or isinstance(value, self.data_type)):
			value = self.data_type(value)
		super(JSONProperty, self).__set__(obj, value)

	def __get__(self, obj, objtype):
		return super(JSONProperty, self).__get__(obj, objtype)

	def default_validator(self, value):
		if value is None or value == self.default_value():
			return
		if not isinstance(value, self.data_type):
			raise TypeError('Validation Error, %s.%s expecting %s, got %s' % (self.model_class.__name__, self.name, self.data_type, type(value)))

	def empty(self, value):
		return not value

	def get_choices(self):
		if callable(self.choices):
			choices = self.choices()
		else:
			choices = self.choices
		if choices:
			choices = [self.make_value_from_datastore(c) for c in choices]
		return choices
