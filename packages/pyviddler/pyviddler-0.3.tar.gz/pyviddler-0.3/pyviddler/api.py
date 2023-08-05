import datetime
import requests
from .exceptions import ViddlerAPIException


class ApiAPI(object):
    """
    The viddler.api.* part of the viddler API
    """
    def __init__(self, apikey, sessionid, endpoint="https://api.viddler.com/api/v2/"):
        self.apikey = apikey
        self.sessionid = sessionid
        self.endpoint = "%sviddler.api.%%s.json" % endpoint

    def _get_params(self, **kwargs):
        """
        convience method to return a dict of querystring parameters with the
        current value of the apikey and session id
        """
        params = {
            'key': self.apikey,
            'sessionid': self.sessionid
        }
        for key, val in kwargs.items():
            if isinstance(val, bool):
                kwargs[key] = int(val)
            elif isinstance(val, (list, tuple)):
                kwargs[key] = ",".join(val)
            elif isinstance(val, (datetime.date, datetime.datetime)):
                kwargs[key] = val.strftime('%Y-%m-%d')
        params.update(kwargs)
        return params

    def _get(self, func, **kwargs):
        url = self.endpoint % func
        params = self._get_params(**kwargs)
        result = requests.get(url, params=params).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result

    def _post(self, func, **kwargs):
        url = self.endpoint % func
        params = self._get_params()
        result = requests.post(url, params=params, data=kwargs).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result

    def echo(self, message):
        return self._get('echo', message=message)['echo_response']

    def getInfo(self):
        return self._get('getInfo')['viddler_api']
