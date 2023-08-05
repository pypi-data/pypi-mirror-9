from .base.obj import BaseObject
from .base.fields import ObjectProperty
from .base.fields import ObjectCollectionProperty


class Variant(BaseObject):

  id = ObjectProperty()
  title = ObjectProperty()
  sku = ObjectProperty()
  weight = ObjectProperty()
  price = ObjectProperty()
  available = ObjectProperty()


class ProductImage(BaseObject):

  filename = ObjectProperty()

  def __str__(self):
    if self._obj_data:
      return self._obj_data.filename
    return ''


class Product(BaseObject):

  id = ObjectProperty()
  handle = ObjectProperty()
  title = ObjectProperty()

  price = ObjectProperty()

  description = ObjectProperty()
  variants = ObjectCollectionProperty(cls=Variant)
  available = ObjectProperty()

  images = ObjectCollectionProperty(cls=ProductImage)
  primary_image = ObjectProperty(cls=ProductImage)

  url = ObjectProperty()


class Category(BaseObject):

  id = ObjectProperty()
  handle = ObjectProperty()
  title = ObjectProperty()
  products = ObjectCollectionProperty(
      cls=Product,
      loader=lambda id_, d: [item for item in d.products if item.category.id == id_])

  url = ObjectProperty()


class Vendor(BaseObject):

  id = ObjectProperty()
  handle = ObjectProperty()
  title = ObjectProperty()
  products = ObjectCollectionProperty(
      cls=Product,
      loader=lambda id_, d: [item for item in d.products if item.vendor.id == id_])

  url = ObjectProperty()
