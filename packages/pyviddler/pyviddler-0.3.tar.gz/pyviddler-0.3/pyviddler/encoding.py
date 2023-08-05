import datetime
import requests
from .exceptions import ViddlerAPIException


class EncodingAPI(object):
    """
    The viddler.api.* part of the viddler API
    """
    def __init__(self, apikey, sessionid, endpoint="https://api.viddler.com/api/v2/"):
        self.apikey = apikey
        self.sessionid = sessionid
        self.endpoint = "%sviddler.encoding.%%s.json" % endpoint

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
            elif val is None:
                del kwargs[key]
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

    def getSettings(self):
        return self._get('getSettings')['encoding_settings']

    def getStatus(self):
        return self._get('getStatus')['list_result']

    def getStatus2(self, video_id=None):
        return self._get('getStatus2')['list_result']

    def encode(self, video_id, profile_id):
        result = self._post('encode', video_id=video_id, profile_id=profile_id)
        return result['list_result']

    def cancel(self, file_id):
        result = self._post('cancel', file_id=file_id)
        return result['list_result']

    def setSettings(self, use_source_for_playback=None, profile_1_bitrate=None,
                    profile_2_bitrate=None, profile_3_bitrate=None,
                    profile_4_bitrate=None):
        result = self._post('setSettings', use_source_for_playback=use_source_for_playback,
            profile_1_bitrate=profile_1_bitrate, profile_2_bitrate=profile_2_bitrate,
            profile_3_bitrate=profile_3_bitrate, profile_4_bitrate=profile_4_bitrate)
        return result['list_result']
