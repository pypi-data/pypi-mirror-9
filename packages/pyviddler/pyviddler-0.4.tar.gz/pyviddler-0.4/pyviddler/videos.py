import datetime
import requests
from .exceptions import ViddlerAPIException


class VideosAPI(object):
    """
    The viddler.videos.* part of the viddler API
    """
    def __init__(self, apikey, sessionid, endpoint="https://api.viddler.com/api/v2/"):
        self.apikey = apikey
        self.sessionid = sessionid
        self.endpoint = "%sviddler.videos.%%s.json" % endpoint

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
        files = kwargs.pop('files', None)
        result = requests.post(url, params=params, data=kwargs, files=files).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result

    ######
    # Ads
    ######

    def getAdsStatus(self, video_id):
        result = self._get('getAdsStatus', video_id=video_id)
        return result['video_ads_status']['status']

    def disableAds(self, *args):
        result = self._post('disableAds', video_ids=",".join(args))
        return result['result']

    def enableAds(self, *args):
        result = self._post('enableAds', video_ids=",".join(args))
        return result['result']

    ######
    # Video Info
    ######

    def search_yourvideos(self, query="*", **kwargs):
        """
        query - string - required (keyword to search for in video title, description, global and timed tags, if all videos send query=*)
        min_upload_date - date - optional (minimum date that the video was uploaded | format: YYYY-MM-DD)
        max_upload_date - date - optional (maximum date that the video was uploaded | format: YYYY-MM-DD)
        max_age - number - optional (videos uploaded in the last 'x' amount of days)
        sort - string - optional (uploaded-desc, upload-asc, views-desc, views-asc, defaults to uploaded-desc)
        per_page - number - optional (defaults to 10, max of 100)
        page - number - optional (defaults to 1)
        """
        kwargs['type'] = 'yourvideos'
        if 'page' not in kwargs:
            results = []
            for i in range(1000):
                kwargs['page'] = i + 1
                result = self._get('search', query=query, **kwargs)
                if result['list_result']['video_list']:
                    results.extend(result['list_result']['video_list'])
                else:
                    return results
        else:
            result = self._get('search', query=query, **kwargs)
            return result['list_result']['video_list']

    def search_user(self, user, **kwargs):
        """
        user - string - required
        sort - string - optional (uploaded-desc, upload-asc, views-desc, views-asc, defaults to uploaded-desc)
        per_page - number - optional (defaults to 10, max of 100)
        page - number - optional (defaults to 1)
        """
        kwargs['type'] = 'user'
        result = self._get('search', user=user, **kwargs)
        return result['list_result']['video_list']

    def search_allvideos(self, query="*", **kwargs):
        """
        query - string - required (keyword to search for in video title, description, global and timed tags, if all videos send query=*)
        sort - string - optional (uploaded-desc, upload-asc, views-desc, views-asc, defaults to uploaded-desc)
        per_page - number - optional (defaults to 10, max of 100)
        page - number - optional (defaults to 1)
        """
        kwargs['type'] = 'allvideos'
        result = self._get('search', query=query, **kwargs)
        return result['list_result']['video_list']

    def getDetails(self, video_id="", url="", **kwargs):
        """
        video_id - string - optional (required if not using url)
        url - string - optional (required if not using video_id)
        status - boolean - optional (False = only files ready to view, True = all files, defaults to False)
        include_comments - boolean - optional (False = no comments (faster response), True = comments (slower response), defaults to False)
        add_comments - boolean - optional (False = no comments (faster response), True = comments (slower response), defaults to False)
        add_embed_code - boolean - optional (False = no embed code, True = embed code, defaults to False)
        add_profile - boolean - optional (False = no profile info, True = profile info, defaults to False)
        add_view_token - boolean - optional (False = no token, True = video token used for viewing, defaults to False)
        """
        if video_id:
            result = self._get('getDetails', video_id=video_id, **kwargs)
        elif url:
            result = self._get('getDetails', url=url, **kwargs)
        else:
            raise ValueError("getDetails requires either the video_id or url.")
        return result['video']

    def getByUser(self, **kwargs):
        """
        page - number - optional (defaults to 1)
        per_page - number - optional (defaults to 10)
        user - string - optional (required if not using sessionid)
        status - boolean - optional
        sort - string - optional (title-asc, title- desc, uploaded-asc, uploaded-desc, views-asc, views-desc, defaults to uploaded-desc)
        tags - list or string - optional
        visibility - list - optional (list of options which are below)
            private = Private Videos
            public = Public Videos
            invite = Invite Only Videos
            embed = Domain Restricted Videos
        """
        raise NotImplementedError

    def setPermalink(self, video_id, permalink=""):
        result = self._get('setPermaLink', video_id=video_id, permalink=permalink)
        return result['video']

    def setDetails(self, video_id, **kwargs):
        """
        video_id - list or string - required (a single or list of video ids to update, if multiple ids are submitted changes will be applied to all videos. Multiple video updates support the following sub-options: age_limit, tags, view_perm, embed_perm, download_perm, commenting_perm, tagging_perm, remove_tags)
        title - string - optional
        description - string - optional
        thumbnail_index - number - optional
        age_limit - number - optional (for users with age gate enabled, - value between 9 and 99 or empty to reset)
        tags - list - optional (list of tags to add. Single video will replace all current tags, multiple videos will append the tags)
        remove_tags - list - optional (list of tags to remove from videos)
        view_perm - string - optional (public, private, invite, embed)
        view_reset_secret - boolean - optional (set to 1 to reset secret key, defaults to 0)
        embed_perm - string - optional (public, private, invite, embed)
        commenting_perm - string - optional (public, private, invite, embed)
        download_perm - string - optional (public, private, invite, embed)
        tagging_perm - string - optional (public, private, invite, embed)
        file_#_flash - boolean - optional (turn flash feature on a file on or off. If video file has been created based on "1" encoding profile - it can't be disabled)
        file_#_iphone - boolean - optional (turn iphone feature on or off)
        file_#_ipad - boolean - optional (turn ipad feature on or off)
        comments_moderation_level - number - optional (0 = no moderation, 1 = hold all comments, 2 = deny comments that may contain profanity, 3 = hold comments that may contain profanity)
        """
        result = self._post('setDetails', video_id=video_id, **kwargs)
        return result['video']

    def setThumbnail(self, video_id, timepoint=None, thumbfile=None):
        if timepoint is None and thumbfile is not None:
            files = {'file': open(thumbfile, 'rb')}
            result = self._post('setThumbnail', video_id=video_id, files=files)
        elif timepoint is not None and thumbfile is None:
            result = self._post('setThumbnail', video_id=video_id, timepoint=timepoint)
        else:
            raise ValueError("You must specify either a timepoint or a file")
        return result['video']

    def delete(self, video_id):
        result = self._post('delete', video_id=video_id)
        return result['success']

    def delFile(self, file_id):
        result = self._post('delete', file_id=file_id)
        return result['video']

    ######
    # Embedding
    ######

    def getEmbedCodeTypes(self):
        result = self._get('getEmbedCodeTypes')
        return result['list_result']['embed_code_types']

    def getEmbedCode(self, video_id, **kwargs):
        """
        video_id - string - required
        width - number - optional
        height - number - optional
        player_type - string - optional (full, simple or mini, defaults to full)
        wmode - string - optional (transparent, opaque, window, defaults to transparent)
        autoplay - boolean - optional
        branding - boolean - optional (show video owner's branding, defaults to true)
        offset - number - optional (playback offset in seconds)
        embed_code_type - number - optional (embed code type number, listed at viddler.videos.getEmbedCodeTypes)
        flashvar - string - optional (can specify any flashvar as the key and it's value as value. IE: displayUser=jeff
        """
        result = self._get('getEmbedCode', video_id=video_id, **kwargs)
        return result['video']['embed_code']

    ######
    # Uploading
    ######

    def prepareUpload(self, allow_replace=False):
        """
        returns {'endpoint': "<where to upload to>", 'token': '<tokenstring>'}
        """
        result = self._get('prepareUpload', allow_replace=allow_replace)
        return result['upload']

    def uploadProgress(self, token):
        result = self._get('uploadProgress', token=token)
        return result['upload_progress']

    def upload_file(self, filepath, title="", description="", allow_replace=False):
        """
        Convenience function to upload a file to Viddler.

        Calls prepareUpload, then submits a POST with the required data and the
        file

        Returns a dict with url, description, thumbnail_url, id, title
        """
        import os
        data = self.prepareUpload(allow_replace)
        # use requests to create the postdata and upload the form
        url = data.pop('endpoint')
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        params = self._get_params()
        _, filename = os.path.split(filepath)
        files = {'file': (filename, open(filepath, 'rb'))}
        result = requests.post(url, params=params, data=data, files=files).json()
        if 'error' in result:
            raise ViddlerAPIException(**result['error'])
        return result['video']


    ######
    # Closed Captioning
    ######

    def addClosedCaptioning(self, video_id, language, closed_captioning_url, default=True):
        result = self._post('addClosedCaptioning', video_id=video_id,
            language=language, closed_captioning_url=closed_captioning_url,
            default=default)
        return result['video']

    def delClosedCaptioning(self, closed_captioning_id):
        result = self._post('delClosedCaptioning', closed_captioning_id=closed_captioning_id)
        return result['video']

    ######
    # Recording
    ######

    def getRecordToken(self):
        result = self._get('getRecordToken')
        return result['record_token']['value']
