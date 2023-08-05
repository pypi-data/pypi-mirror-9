import os
import json

from flask import current_app as app

CREDENTIALS_PATH = os.path.expanduser('~/.boutique')


class ApiCredentials():
  
  def __init__(self, path):
    self._path = path
    self._email = None
    self._token = None
    
    if os.path.exists(path):
      with open(path, "r") as f:
        credentials_json = json.load(f)
        self._email = credentials_json.get('email')
        self._token = credentials_json.get('token')
        
  def set(self, email, token):
    self._email = email
    self._token = token
    
    with open(self._path, "w") as f:
      os.chmod(self._path, 0600)
      json.dump({'email':self._email, 'token':self._token}, f)
  
  @property
  def email(self):
    return self._email
  
  @property
  def token(self):
    return self._token

  @property
  def access_cookie(self):
    return app.config.get('X_BF_ACCESS')


def load():
  credentials = ApiCredentials(CREDENTIALS_PATH)
  return credentials
