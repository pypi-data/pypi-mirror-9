import requests, json
from urllib import urlencode
from _required_fields import check_required
from response import FoxtrotResponse

class Foxtrot(object):
  """Foxtrot API Client"""

  host = 'api.foxtrot.io'
  ssl = True
  api_root = ''

  def __init__(self, api_key, version='v1'):
    self.api_key = api_key
    self.version = version
    self.headers = {'content-type': 'application/json'}

  def _build_url(self, endpoint, args):
    proto = "https" if self.ssl else "http"
    args['key'] = self.api_key
    query = urlencode(args)
    return "{0}://{1}{2}/{3}/{4}?{5}".format(proto, self.host, self.api_root, self.version, endpoint, query)

  def get(self, endpoint, args):
    url = self._build_url(endpoint, args)
    response = requests.get(url, headers=self.headers)
    return response.json()

  def post(self, endpoint, data, args):
    url = self._build_url(endpoint, args)
    response = requests.post(url, data=json.dumps(data), headers=self.headers)
    return response.json()

  def poll(self, txid, args={}):
    resp = self.get('poll', {'txid': txid})
    return FoxtrotResponse.response_for('poll', resp, self)

  @check_required
  def optimize(self, data, args={}):
    resp = self.post('optimize', data, args)
    return FoxtrotResponse.response_for('optimize', resp, self)
