from flask import Flask

from boutiqueclient.bsite import views


DEFAULT_CONFIG = {
  'API_ENDPOINT': 'https://boutiqueforge.com',
  'SITE_API_ENDPOINT': 'http://%s.app.boutiqueforge.com',
}


def create_app():
  app = Flask(__name__, instance_relative_config=True)
  configure_app(app)
  configure_views(app)
  return app


def configure_app(app):
  app.config.update(DEFAULT_CONFIG)
  app.config.from_pyfile('app.cfg', silent=True)


def configure_views(app):
  app.add_url_rule('/', 'index', views.index)
  app.add_url_rule('/pages/<page_name>', 'page', views.page)
  app.add_url_rule('/products/<product_name>', 'product', views.product)
  app.add_url_rule('/vendors/<vendor_name>', 'vendor', views.vendor)
  app.add_url_rule('/categories/<category_name>', 'category', views.category)
  app.add_url_rule('/assets/<path:asset_name>', 'asset', views.asset)
  app.add_url_rule('/cart', 'cart', views.cart,
                   methods=('GET', 'POST'))
  app.add_url_rule('/cart/add', 'cart_add', views.cart_add,
                   methods=('GET','POST'))
  app.add_url_rule('/cart/change', 'cart_change', views.cart_change)
