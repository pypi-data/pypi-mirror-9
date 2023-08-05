from flask import current_app as app
from flask import send_from_directory
from flask import g
from flask import request
from flask import make_response
from flask import redirect
from flask import url_for

from boutiqueclient.bsite.template import render_template
from boutiqueclient.bsite import objects
from boutiqueclient.bsite.objects import db


def index():
  data = db.load()
  site_obj = objects.Site(data.site, data)
  g.site = site_obj
  return render_template('index.html', site=site_obj, cart=objects.Cart())


def page(page_name):
  if not page_name.endswith('.html'):
    page_name = '%s.html' % page_name

  data = db.load()
  site_obj = objects.Site(data.site, data)
  g.site = site_obj
  return render_template(page_name, site=site_obj, cart=objects.Cart())


def product(product_name):
  data = db.load()
  site_obj = objects.Site(data.site, data)
  g.site = site_obj
  product_obj = site_obj.products[product_name]
  return render_template('product.html', site=site_obj, cart=objects.Cart(), product=product_obj)


def vendor(vendor_name):
  data = db.load()
  site_obj = objects.Site(data.site, data)
  g.site = site_obj
  vendor_obj = site_obj.vendors[vendor_name]
  return render_template('vendor.html', site=site_obj, cart=objects.Cart(), vendor=vendor_obj)


def category(category_name):
  data = db.load()
  site_obj = objects.Site(data.site, data)
  g.site = site_obj
  category_obj = site_obj.categories[category_name]
  return render_template('category.html', site=site_obj, cart=objects.Cart(), category=category_obj)


def collection(collection_name):
  data = db.load()
  site_obj = objects.Site(data.site, data)
  g.site = site_obj
  collection_obj = site_obj.collections[collection_name]
  return render_template('collection.html', site=site_obj, cart=objects.Cart(), collection=collection_obj)


def asset(asset_name):
  return send_from_directory(app.assets_folder, asset_name)


def cart():
  if request.method == 'GET':
    data = db.load()
    site_obj = objects.Site(data.site, data)
    g.site = site_obj
    return render_template('cart.html', site=site_obj, cart=objects.Cart())
  else:
    return redirect(url_for('.cart'))


def cart_add():
  resp = make_response(redirect(url_for('.cart')))
  return resp


def cart_change():
  resp = make_response(redirect(url_for('.cart')))
  return resp
