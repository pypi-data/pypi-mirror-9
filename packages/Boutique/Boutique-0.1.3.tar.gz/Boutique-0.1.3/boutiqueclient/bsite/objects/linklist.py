from .base.obj import BaseObject
from .base.fields import ObjectProperty, ObjectCollectionProperty


class Link(BaseObject):

  title = ObjectProperty()
  url = ObjectProperty()

  def __str__(self):
    if self._obj_data:
      return self._obj_data.title


class LinkList(BaseObject):

  id = ObjectProperty()
  handle = ObjectProperty()
  title = ObjectProperty()
  links = ObjectCollectionProperty(cls=Link)

  def __str__(self):
    if self._obj_data:
      return self._obj_data.title
