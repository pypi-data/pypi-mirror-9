from flask.ext.script import Command

from boutiqueclient.bservice.api.service import BoutiqueService


class BaseCommand(Command):

  def __init__(self):
    self._service = BoutiqueService()
