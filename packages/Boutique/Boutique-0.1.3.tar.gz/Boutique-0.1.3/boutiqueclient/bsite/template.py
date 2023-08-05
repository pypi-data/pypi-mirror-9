from flask import abort
from flask import current_app as app
from jinja2 import TemplateNotFound
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment


from boutiquecommons.template.filters import get_filters


def render_template(template_name_or_list, **context):
  env = SandboxedEnvironment(loader=FileSystemLoader(app.template_folder))
  env.filters.update(get_filters())
  
  try:
    template = env.get_or_select_template(template_name_or_list)
  except TemplateNotFound:
    abort(404)
  return template.render(**context)
