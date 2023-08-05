import os
import json

from flask import current_app as app


class TreeNode(object):

  def __init__(self, data):
    assert isinstance(data, dict)
    self._data = data

  def __getattr__(self, key):
    if key in self._data:
      item = self._data.get(key)
      if isinstance(item, dict):
        item = TreeNode(item)
      elif isinstance(item, list):
        item = [TreeNode(list_item) for list_item in item]
      return item
    return None

  def __getitem__(self, key):
    return self._data.__getitem__(key)

  def __str__(self):
    return str(self._data)


def _data_file_path():
  boutiquedata_path = os.path.join(app.app_folder, '.boutiquedata')
  return boutiquedata_path


def load_as_dict():
  path = _data_file_path()
  if not os.path.isfile(path):
    return None

  with open(path) as f:
    data = json.load(f)
  return data


def load():
  return TreeNode(load_as_dict())


def save(data_dict):
  assert isinstance(data_dict, dict)
  with open(_data_file_path(), 'w+') as f:
    f.write(json.dumps(data_dict))
