class ApiError(IOError):
  
  pass


class ApiJsonError(ApiError):
  
  def __init__(self, response):
    super(ApiJsonError, self).__init__(response.prettyprint())


class ApiUnauthorizedError(ApiError):
  
  pass
