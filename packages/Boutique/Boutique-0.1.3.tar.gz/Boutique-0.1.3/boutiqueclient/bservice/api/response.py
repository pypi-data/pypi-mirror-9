from boutiqueclient.bservice.api.error import ApiJsonError


class ApiResponse(object):

  def __init__(self, response):
    self._response = response

  @property
  def content(self):
    return self._response.content

  def json(self):
    try:
      return self._response.json()
    except ValueError:
      raise ApiJsonError(self)

  @property
  def status_code(self):
    return self._response.status_code

  @property
  def error(self):
    error = self.get('error', None)
    if error is not None:
      return error

    errors = self.get('errors', [])
    if len(errors) > 0:
      return errors[0]

    return None

  def is_success(self):
    if self._response.status_code >= 200 and self._response.status_code < 300:
      return True
    return False

  def is_error(self):
    return not self.is_success()

  def is_unauthorized(self):
    return self.status_code == 401

  def get(self, key, default=None):
    response_json = self.json()
    return response_json.get(key, default)

  def prettyprint(self):
    s = "{url}\n{content}".format(url=self._response.url, content=self._response.content)
    return s
