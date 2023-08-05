from .base.obj import BaseObject
from .base.fields import ObjectProperty, ObjectCollectionProperty
from .product import Product, Vendor, Category
from .linklist import LinkList


class Site(BaseObject):

  name = ObjectProperty()
  title = ObjectProperty()

  preferred_url = ObjectProperty()
  permanent_url = ObjectProperty()

  products = ObjectCollectionProperty(
      cls=Product,
      loader=lambda id_, d: d.products)
  vendors = ObjectCollectionProperty(
      cls=Vendor,
      loader=lambda id_, d: d.vendors)
  categories = ObjectCollectionProperty(
      cls=Category,
      loader=lambda id_, d: d.categories)
  linklists = ObjectCollectionProperty(
      cls=LinkList,
      loader=lambda id_, d: d.linklists)

  currency = ObjectProperty()
  unit_system = ObjectProperty()
