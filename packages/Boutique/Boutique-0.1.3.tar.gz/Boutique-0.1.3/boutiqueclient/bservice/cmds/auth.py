import sys
import getpass

from path import path

from boutiqueclient.bservice.api.error import ApiUnauthorizedError
from .base import BaseCommand


class Login(BaseCommand):
  """Log in with your boutique credentials."""

  def run(self):
    success = False
    retries, retry = 3, 0

    sys.stdout.write('Enter your boutiqueforge.com credentials.\n')
    sys.stdout.write('Email: ')

    email = sys.stdin.readline().strip()
    token = None

    while retry < retries and not success:
      password = getpass.getpass('Password: ')
      resp = self._service.post('/api/account/login',
        data=dict(email=email, password=password))

      if resp.is_success():
        success = True
        resp_json = resp.json()
        token = resp_json.get('account', {}).get('api_token')

        print 'Authentication successful!'
        break
      elif resp.status_code == 412:
        print resp.get('error')
        return
      else:
        retry += 1

    if not success:
      print 'Could not login'
      return

    # save the netrc email and token in the .netrc file
    self._update_credentials(email, token)

    # send the pubfile to the server so git ssh authentication will work
    self._upload_pubfile()

  def _update_credentials(self, email, token):
    self._service.credentials.set(email, token)

  def _upload_pubfile(self):
    file_path = path('~/.ssh/id_rsa.pub').expanduser()
    if not file_path.isfile():
      print 'Could not find public ssh key, skipping uploading of key...'
      return

    with open(file_path, 'r') as f:
      publickey = f.read()

    data = {'publickey': publickey}
    resp = self._service.post('/api/account/publickey', data)
    if not resp.is_success():
      print 'Could not upload public key: %s' % resp.error


class Whoami(BaseCommand):
  """Print the user you're currently logged in with."""

  def run(self):
    email = self._service.credentials.email
    token = self._service.credentials.token

    if email is None or token is None:
      raise ApiUnauthorizedError()

    print email
