import requests
from .exceptions import ViddlerAPIException


class UsersAPI(object):
    """
    The viddler.users.* part of the viddler API
    """
    def __init__(self, apikey, sessionid="", endpoint="https://api.viddler.com/api/v2/"):
        self.apikey = apikey
        self.sessionid = sessionid
        self.endpoint = "%sviddler.users.%%s.json" % endpoint

    def _get_params(self, **kwargs):
        """
        convience method to return a dict of querystring parameters with the
        current value of the apikey and session id
        """
        params = {'key': self.apikey}
        if self.sessionid:
            params['sessionid'] = self.sessionid

        params.update(kwargs)
        return params

    def auth(self, username, password):
        url = self.endpoint % 'auth'
        params = self._get_params(username=username, password=password)
        result = requests.get(url, params=params).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        self.sessionid = result['auth']['sessionid']
        return self.sessionid

    def getProfile(self, user=""):
        url = self.endpoint % "getProfile"
        if user:
            params = self._get_params(user=user)
        else:
            params = self._get_params()
        result = requests.get(url, params=params).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result['user']

    def setProfile(self, **kwargs):
        valid_keys = ('first_name', 'last_name', 'about_me', 'city', 'company',
                      'age', 'gender', 'homepage', 'avatar_url')
        url = self.endpoint % "setProfile"
        params = self._get_params()
        for key in valid_keys:
            if key in kwargs:
                params[key] = kwargs[key]
        result = requests.post(url, data=params).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result['user']

    def logout(self):
        url = self.endpoint % "logout"
        result = requests.get(url, params=self._get_params()).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result['success']

    def register(self, **kwargs):
        raise NotImplementedError

    def getSettings(self):
        url = self.endpoint % "getSettings"
        result = requests.get(url, params=self._get_params()).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result['settings']

    def setSettings(self, **kwargs):
        """
        visible - boolean - optional (0 = private, 1 = public)
        gravatar - boolean - otional (0 = do not use gravatar, 1 = use gravatar)
        default_view_permission - string - optional (private, invite, embed, public)
        default_comment_permission - string - optional (private or public)
        default_download_permission - string - optional (private or public)
        default_embed_permission - string - optional (private or public)
        default_tag_permission - string - optional (private or public)
        whitelisted_domains - string - optional (Comma delimited list of whitelisted domains - max 1024 characters)
        clicking_through_enabled - boolean - optional (0 = no click-throughs from video, 1 = click-throughs enabled)
        video_browser_enabled - boolean - optional (0 = do not show videos at the end of the video, 1 = show videos)
        embed_code_type - integer - optional (1 = Legacy, 2 = WordPress, 3 = Flash w/ HTML5 Fallback, 5 = iframe - You must have access to multiple embed types to update correctly)
        video_delivery_method - number - optional (0 = Progressive Download, 1 = RTMP Streaming | You must have access to both delivery methods to be able to change)
        hd_playback - boolean - optional (0 = do not allow your users to view in HD, 1 = allow)
        mobile_playback - boolean - optional (0 = do not allow your users to view on mobile devices 1 = allow)
        default_video_permalink - string - optional
        custom_embed_url - string - optional (The custom url to use for your embeds, you must set the URLs cname to viddler.com for this to work)
        comments_moderation - number - optional (0 = no moderation, 1 = Hold all comments, 2 = Automatically deny posts that may profanity, 3 = Hold all posts that may contain profanity)
        video_delivery_method - number - optional (0 = progressive, 1 = streaming, 3 = adaptive)
        default_tags -string - optional (comma-delimited list of tags to be applied to all newly uploaded videos. Can only be used if your account has access to this feature)
        email_encoding_end - boolean - optional (0 = do not email me when my encodes are finished, 1 = email me)
        email_comment_received - boolean - optional (0 = do not email me when comments are received, 1 = email me)
        email_tag_added - boolean - optional (0 = do not email me when tags are received, 1 = email me)
        email_commented_video_received_comment - boolean - optional (0 = do not email me when a video comment is posted, 1 = email me)
        email_newsletter - boolean - optional (0 = do not subscribe to newsletter, 1 = subscribe)
        """
        raise NotImplementedError

    def getPlayerBranding(self):
        url = self.endpoint % "getPlayerBranding"
        result = requests.get(url, params=self._get_params()).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        print result
        return result['player_branding']

    def setPlayerBranding(self, **kwargs):
        """
        logo_url - string - optional (URL to the logo to use for your player)
        logo_click_url - string - optional (URL for the logo to click through to. Leave blank for no click through)
        logo_offset_x - number - optional (Total pixels to offset your logo from the player on the x axis)
        logo_offset_y - number - optional (Total pixels to offset your logo from the player on the y axis)
        logo_align - string - optional (Aligns your logo (choices: br, bl, tl, tr)
        logo_visible - boolean - optional (Whether or not to show your logo)
        shade_dark - boolean - optional (Set to true to use a darker shade, false to use a lighter shade)
        enable_stripes - boolean - optional (Whether or not to use stripes in the load bar)
        simple_color - color - optional (Main player color)
        control_bar - color - optional (Main control bar color)
        bhover - color - optional (Button hover color)
        bidle - color - optional (Button idle color)
        bclicked - color - optional (Button clicked color)
        phover - color - optional (Plus button hover color)
        pidle - color - optional (Plus button idle color)
        pclicked - color - optional (Plus button clicked color)
        timeplayed - color - optional (Time played bar color)
        timeloaded - color - optional (Time loaded bar color)
        timebackground - color - optional (Time bar background color)
        """
        raise NotImplementedError
