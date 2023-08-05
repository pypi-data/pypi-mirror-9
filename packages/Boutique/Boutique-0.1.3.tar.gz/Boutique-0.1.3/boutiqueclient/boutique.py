#!/usr/bin/env python
import sys

from flask.ext import script
from flask.ext.script import Manager

from boutiqueclient.app import create_app
from boutiqueclient.bservice.api.error import ApiUnauthorizedError, ApiError
from boutiqueclient.bservice.cmds import Login
from boutiqueclient.bservice.cmds import Whoami
from boutiqueclient.bservice.cmds import List
from boutiqueclient.bservice.cmds import Create
from boutiqueclient.bservice.cmds import Delete
from boutiqueclient.bservice.cmds import Deploy
from boutiqueclient.bservice.cmds import BoutiqueServer
from boutiqueclient.bservice.cmds.server import AppNotValid

app = create_app()


def main():
  manager = Manager(app, with_default_commands=False)
  manager.add_command('runserver', BoutiqueServer())
  manager.add_command('login', Login())
  manager.add_command('whoami', Whoami())
  manager.add_command('list', List())
  manager.add_command('create', Create())
  manager.add_command('delete', Delete())

  try:
    manager.run()
  except ApiUnauthorizedError:
    print 'You are not logged in. Use: boutique login'
    sys.exit(1)
  except ApiError, e:
    print e.message
    sys.exit(1)
  except AppNotValid, e:
    print e.message
    sys.exit(1)
  except KeyboardInterrupt:
    sys.exit(1)


if __name__ == "__main__":
  main()
