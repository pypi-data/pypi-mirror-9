import os
import re
import sys
import subprocess

from flask.ext.script import Server, Option
from werkzeug._internal import _log
from requests.exceptions import RequestException

from boutiqueclient.bservice.api.service import BoutiqueService
from boutiqueclient.bsite.objects import db
from boutiquecommons import datetimeutil


_SITE_NAME_RE = re.compile(r"origin\s+git@boutique.+\.com:(.+)\.git")

_UPDATED_KEY = 'updated'

_SITE_UPDATED_KEY = 'site_updated'
_SITE_KEY = 'site'
_PRODUCTS_UPDATED_KEY = 'products_updated'
_PRODUCTS_KEY = 'products'
_VENDORS_UPDATED_KEY = 'vendors_updated'
_VENDORS_KEY = 'vendors'
_CATEGORIES_UPDATED_KEY = 'categories_updated'
_CATEGORIES_KEY = 'categories'
_LINKLISTS_UPDATED_KEY = 'linklists_updated'
_LINKLISTS_KEY = 'linklists'

def _templates_path(app_path):
    return os.path.abspath(os.path.join(app_path, 'templates'))


def _assets_path(app_path):
  return os.path.abspath(os.path.join(app_path, 'assets'))


def _check_app_path(app_path):
    templates_path = _templates_path(app_path)
    if not os.path.isdir(templates_path):
      raise AppNotValid()


class AppNotValid(Exception):

  message = 'Could not find a valid boutique app at the specified path.'


class BoutiqueServer(Server):

  description = 'Run your boutique on localhost.'

  def __init__(self, **kwargs):
    kwargs.setdefault('port', 9000)
    super(BoutiqueServer, self).__init__(**kwargs)

    self._service = BoutiqueService()

  def get_options(self):
    options = super(BoutiqueServer, self).get_options()
    options += (
      Option('app_path',
           type=unicode,
           nargs='?',
           default=os.getcwd()),
    )
    return options

  def __call__(self, app, app_path, **kwargs):
    app.template_folder = _templates_path(app_path)
    app.assets_folder = _assets_path(app_path)
    app.app_folder = app_path
    app.debug = True

    with app.app_context():
      _check_app_path(app_path)
      self._download_data(app_path)

    return super(BoutiqueServer, self).__call__(app, **kwargs)

  def _update_data_if_necessary(self, data, field_key, field_updated_key,
                                default, site_name, version_resp, api_endpoint):
    assert isinstance(data, dict)
    assert isinstance(field_key, basestring)
    assert isinstance(field_updated_key, basestring)
    assert isinstance(site_name, basestring)
    assert isinstance(api_endpoint, basestring)

    version_json = version_resp.json()

    obj_updated = datetimeutil.isoformat_to_datetime(
          version_json.get(field_key, {}).get(_UPDATED_KEY))
    obj_updated_local = datetimeutil.isoformat_to_datetime(
          data.get(field_updated_key))

    if not data or not obj_updated_local or obj_updated > obj_updated_local:
      _log('info', ' * Downloading latest %s data...' % field_key)
      obj_resp = self._service.site_get(site_name, api_endpoint)
      data[field_key] = obj_resp.json().get(field_key, default)
      data[field_updated_key] = datetimeutil.datetime_to_isoformat(
          obj_updated)

  def _download_data(self, app_path):
    proc = subprocess.Popen(['git', 'remote', '-v'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=app_path)
    proc.wait()

    output = proc.stdout.read()
    match = _SITE_NAME_RE.search(output)
    if not match:
      raise AppNotValid()
    site_name = match.group(1)

    try:
      data = db.load_as_dict() or {}

      version_resp = self._service.site_get(site_name, '/api/data/version')

      self._update_data_if_necessary(
          data, _SITE_KEY, _SITE_UPDATED_KEY, None, site_name,
          version_resp, '/api/site')
      self._update_data_if_necessary(
          data, _PRODUCTS_KEY, _PRODUCTS_UPDATED_KEY, [], site_name,
          version_resp, '/api/products')
      self._update_data_if_necessary(
          data, _VENDORS_KEY, _VENDORS_UPDATED_KEY, [], site_name,
          version_resp, '/api/vendors')
      self._update_data_if_necessary(
          data, _CATEGORIES_KEY, _CATEGORIES_UPDATED_KEY, [], site_name,
          version_resp, '/api/categories')
      self._update_data_if_necessary(
          data, _LINKLISTS_KEY, _LINKLISTS_UPDATED_KEY, [], site_name,
          version_resp, '/api/linklists')

      db.save(data)

    except RequestException:
      print "Failed to contact boutiqueforge.com server."
      sys.exit(1)

    return data
