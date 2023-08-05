import types

from .obj import ObjectCollection


class BaseProperty(object):

  def contribute_to_class(self, cls, name):
    self.name = name
    cls._meta.add_field(self)

  def get_value(self, obj):
    raise NotImplementedError


class ObjectProperty(BaseProperty):

  def __init__(self, field=None, cls=None):
    super(ObjectProperty, self).__init__()
    self._model_field_name = field
    self._prop_cls = cls

  def get_value(self, obj):
    field_name = self._model_field_name or self.name
    prop = getattr(obj._obj_data, field_name)

    if isinstance(property, types.MethodType):
      prop = prop()

    if prop and self._prop_cls:
      prop = self._prop_cls(prop, obj._all_data)

    return prop


class ObjectCollectionProperty(ObjectProperty):

  def __init__(self, cls, loader=None, key='handle', *args, **kwargs):
    super(ObjectCollectionProperty, self).__init__(*args, **kwargs)
    self._obj_class = cls
    self._key_name = key
    self._items_loader = loader

  def get_value(self, obj):
    if self._items_loader:
      items = self._items_loader(obj._obj_data.id, obj._all_data)
    else:
      items = super(ObjectCollectionProperty, self).get_value(obj)
    return ObjectCollection(cls=self._obj_class,
                            items=items,
                            key=self._key_name,
                            all_data=obj._all_data)
