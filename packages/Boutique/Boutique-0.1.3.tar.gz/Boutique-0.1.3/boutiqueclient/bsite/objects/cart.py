from .base.obj import BaseObject


class Cart(BaseObject):

  def __init__(self):
    super(Cart, self).__init__({}, {})

  @property
  def items(self):
    return []

  @property
  def items_count(self):
    return 0

  @property
  def url(self):
    return "/cart"

  @property
  def add_url(self):
    return "/cart/add"

  @property
  def change_url(self):
    return "/cart/add"

  @property
  def total_price(self):
    return 0
