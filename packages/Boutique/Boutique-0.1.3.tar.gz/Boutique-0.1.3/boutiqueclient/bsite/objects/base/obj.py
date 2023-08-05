class BaseObjectMeta(object):

  def __init__(self):
    self.fields = []
    self.name = None

  def contribute_to_class(self, cls, name):
    cls._meta = self
    self.name = cls.__name__.lower()

  def add_field(self, field):
    self.fields.append(field)

  def get_field(self, name):
    for f in self.fields:
      if f.name == name:
        return f
    return None


class BaseObjectMetaclass(type):

  def __new__(cls, name, bases, attrs):
    module = attrs.pop('__module__')
    new_class = super(BaseObjectMetaclass, cls).__new__(cls, name, bases, {'__module__': module})

    new_class.add_to_class('_meta', BaseObjectMeta())
    for obj_name, obj in attrs.items():
      new_class.add_to_class(obj_name, obj)

    return new_class

  def add_to_class(cls, name, value):
    if hasattr(value, 'contribute_to_class'):
      value.contribute_to_class(cls, name)
    else:
      setattr(cls, name, value)


class BaseObject(object):

  __metaclass__ = BaseObjectMetaclass

  def __init__(self, obj_data, all_data):
    self._obj_data = obj_data
    self._all_data = all_data

  def __getattr__(self, name):
    if name.startswith('_'):
      return object.__getattribute__(self, name)

    field = self._meta.get_field(name)
    if field is None:
      return None

    return field.get_value(self)


class ObjectIterator(object):

  def __init__(self, cls, items_iterator, all_data):
    self._obj_class = cls
    self._items_iterator = items_iterator
    self._all_data = all_data

  def next(self):
    item = self._items_iterator.next()
    if item is None:
      return None
    return self._obj_class(item, self._all_data)


class ObjectCollection(object):

  def __init__(self, cls, items, key, all_data):
    self._obj_class = cls
    self._items = items
    self._key_name = key
    self._all_data = all_data

  def __unicode__(self):
    return str(self._items)

  def __iter__(self):
    return ObjectIterator(cls=self._obj_class,
                items_iterator=self._items.__iter__(),
                all_data=self._all_data)

  def __len__(self):
    return len(self._items)

  def __getitem__(self, key):
    if isinstance(key, slice):
      return ObjectCollection(cls=self._obj_class,
                  items=self._items[key],
                  key=self._key_name,
                  all_data=self._all_data)
    else:
      key = str(key)
      for item in self._items:
        if self.__equal_keys(str(getattr(item, self._key_name)), key):
          return self._obj_class(item, self._all_data)
      return None

  @staticmethod
  def __equal_keys(key1, key2):
    return key1.replace("_", "-") == key2.replace("_", "-")

  @property
  def first(self):
    if not self._items:
      return None
    return self._obj_class(self._items[0], self._all_data)

  @property
  def last(self):
    if not self._items:
      return None
    return self._obj_class(self._items[-1], self._all_data)
