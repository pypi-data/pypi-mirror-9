import requests, json, types, re, copy
from urllib import urlencode
from response import FoxtrotResponse
from errors import ParameterError

class Foxtrot(object):
  """Foxtrot API Client"""

  host = 'api.foxtrot.io'
  ssl = True
  api_root = ''

  def __init__(self, api_key, version='v1'):
    self.api_key = api_key
    self.version = version
    self.headers = {'content-type': 'application/json'}
    self.__set_methods(self.__fetch_methods())

  def _proto(self):
    return "https" if self.ssl else "http"

  def _build_url(self, endpoint, args):
    args['key'] = self.api_key
    query = urlencode(args)
    return "{0}://{1}{2}/{3}/{4}?{5}".format(self._proto(), self.host, self.api_root, self.version, endpoint, query)

  def __make_request_no_data(self, method, endpoint, args):
    url = self._build_url(endpoint, args)
    response = getattr(requests, method)(url, headers=self.headers)
    return response.json()

  def __make_request_data(self, method, endpoint, data, args):
    url = self._build_url(endpoint, args)
    response = getattr(requests, method)(url, data=json.dumps(data), headers=self.headers)
    return response.json()

  def get(self, endpoint, data, args):
    args.update(data)
    return self.__make_request_no_data('get', endpoint, args)

  def delete(self, endpoint, data, args):
    args.update(data)
    return self.__make_request_no_data('delete', endpoint, args)

  def post(self, endpoint, data, args):
    return self.__make_request_data('post', endpoint, data, args)

  def put(self, endpoint, data, args):
    return self.__make_request_data('put', endpoint, data, args)

  def patch(self, endpoint, data, args):
    return self.__make_request_data('patch', endpoint, data, args)

  def poll(self, txid):
    return self.get_poll(txid=txid)

  def __fetch_methods(self):
    resp = requests.get("{0}://{1}{2}/{3}/endpoints".format(self._proto(), self.host, self.api_root, self.version))
    return resp.json()['endpoints'][self.version]

  def __create_method(self, endpoint, original_endpoint_name, endpoint_method_name, http_method):
    url_params = re.findall(r'<(.*)>', endpoint['path'])
    def f(self, *args, **kwargs):
      if len(args) == 1 and len(kwargs) == 0:
        kwargs = args[0]
      for param in (endpoint['params'][http_method] + url_params):
        if param not in kwargs:
          raise ParameterError(param)
      endpoint_name = copy.copy(original_endpoint_name)
      for param in url_params:
        endpoint_name = endpoint_name.replace('_<{}>'.format(param), '/{}'.format(kwargs[param]))
        del kwargs[param]
      query = kwargs.pop('_query', {})
      resp = getattr(self, http_method.lower())(endpoint_name, kwargs, query)
      return FoxtrotResponse.response_for(endpoint_name, resp, self)
    f.__name__ = str(endpoint_method_name)
    f.__doc__ = endpoint['description'][http_method]
    return f

  def __set_method(self, endpoint):
    for http_method in endpoint['methods']:
      endpoint_name = (endpoint['path']
                      .replace(self.api_root, '', 1)
                      .replace('/{}/'.format(self.version), '', 1)
                      .replace('/', '_'))
      endpoint_method_name = http_method.lower() + '_' + re.sub(r'_<(.*)>', '', endpoint_name)
      method = types.MethodType(self.__create_method(endpoint, endpoint_name,
                endpoint_method_name, http_method), self)
      setattr(self, endpoint_method_name, method)

  def __set_methods(self, endpoints):
    for endpoint in endpoints.values():
      if 'url' in endpoint:
        self.__set_method(endpoint)
      else:
        self.__set_methods(endpoint)
