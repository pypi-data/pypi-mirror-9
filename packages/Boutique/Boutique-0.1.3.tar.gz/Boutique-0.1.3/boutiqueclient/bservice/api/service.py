import base64
import urlparse
import requests

from flask import current_app as app

from boutiqueclient.bservice.api.response import ApiResponse
from boutiqueclient.bservice.api.error import ApiUnauthorizedError
from boutiqueclient.bservice.api import credentials


_API_ENDPOINT_KEY = 'API_ENDPOINT'
_SITE_API_ENDPOINT_KEY = 'SITE_API_ENDPOINT'


class BoutiqueService(object):

  def __init__(self):
    self._credentials = credentials.load()

  @property
  def credentials(self):
    return self._credentials

  @property
  def _api_hostname(self):
    host = urlparse.urlparse(app.config[_API_ENDPOINT_KEY]).hostname
    return host

  @property
  def _headers(self):
    headers = {}
    email, token = self._credentials.email, self._credentials.token
    if email is not None and token is not None:
      authorization_value = base64.b64encode('%s:%s' % (email, token))
      authorization_header_value = 'Basic %s' % authorization_value
      headers['Authorization'] = authorization_header_value

    return headers

  @property
  def _cookies(self):
    cookies = {}
    access_cookie = self._credentials.access_cookie
    if access_cookie is not None:
      cookies['X_BF_ACCESS'] = access_cookie
    return cookies

  def get(self, path, data={}):
    url = '%s%s' % (app.config[_API_ENDPOINT_KEY], path)
    resp = requests.get(url, data=data, headers=self._headers, cookies=self._cookies)
    return self._handle_response(resp)

  def site_get(self, site_name, path, data={}):
    url = '%s%s' % (app.config[_SITE_API_ENDPOINT_KEY] % site_name, path)
    resp = requests.get(url, data=data, headers=self._headers, cookies=self._cookies)
    return self._handle_response(resp)

  def post(self, path, data={}):
    url = '%s%s' % (app.config[_API_ENDPOINT_KEY], path)
    resp = requests.post(url, data=data, headers=self._headers, cookies=self._cookies)
    return self._handle_response(resp)

  def delete(self, path):
    url = '%s%s' % (app.config[_API_ENDPOINT_KEY], path)
    resp = requests.delete(url, headers=self._headers, cookies=self._cookies)
    return self._handle_response(resp)

  def _handle_response(self, response):
    api_response = ApiResponse(response)
    if api_response.is_unauthorized():
      raise ApiUnauthorizedError()
    return api_response
