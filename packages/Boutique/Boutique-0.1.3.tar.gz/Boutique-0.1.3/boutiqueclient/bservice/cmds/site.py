from flask.ext.script import Option

from boutiqueclient.bservice.api.error import ApiError
from .base import BaseCommand


class List(BaseCommand):
  """List sites for current user."""

  def run(self):
    resp = self._service.get('/api/site')
    if resp.is_success():
      sites = resp.get('sites', [])
      if len(sites) > 0:
        for site in sites:
          print site.get('name')
      else:
        print 'You do not have any sites created'
    else:
      raise ApiError(resp.error)


class Create(BaseCommand):
  """Create a new site."""

  option_list = (
    Option('name', type=unicode),
  )

  def run(self, name):
    data = {'name': name}
    resp = self._service.post('/api/site', data=data)
    if resp.is_success():
      resp_json = resp.json()
      site = resp_json.get('site', {})
      print 'Site %s was successfuly created!' % site.get('name')
      print 'HTTP: %s' % site.get('url')
      print 'GIT:  %s' % site.get('git_url')
    else:
      raise ApiError(resp.error)


class Delete(BaseCommand):
  """Delete an existing site."""

  option_list = (
      Option('name', type=unicode),
  )

  def run(self, name):
    resp = self._service.delete('/api/site/%s' % name)
    if resp.is_success():
      print 'Site was successfuly deleted!'
    else:
      raise ApiError(resp.error)


class Deploy(BaseCommand):
  """Deploy an existing site."""

  option_list = (
      Option('name', type=unicode),
  )

  def run(self, name):
    resp = self._service.post('/api/site/%s/deploy' % name)
    if resp.is_success():
      resp_json = resp.json()
      deployment = resp_json.get('site', {}).get('deployment', {})
      print 'Successfully deployed site %s, commit %s!' % \
          (name, deployment.get('hash'))
    else:
      raise ApiError(resp.error)
