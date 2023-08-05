class FoxtrotError(RuntimeError):
  def __init__(self, message):
    super(FoxtrotError, self).__init__(message)

class ParameterError(FoxtrotError):
  def __init__(self, param):
    self.parameter = param
    super(ParameterError, self).__init__("Missing parameter: {}".format(param))

class APIResponseError(FoxtrotError):
  pass

class APITimeoutError(FoxtrotError):
  def __init__(self, count):
    self.count = count
    super(APITimeoutError, self).__init__("Request timed out after {} seconds.".format(count))
