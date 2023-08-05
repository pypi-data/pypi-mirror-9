import urllib


class AbstractOAuth(object):

    def __init__(self, client_id, callback, scope):
        self._client_id = client_id
        self._callback = callback
        self._scope = scope

    def _format_url(self, path, params=None):
        params = params or dict()
        query = urllib.urlencode(params)
        separator = "?" if query else ""
        url = path + separator + query
        return url

    def get_url(self):
        raise NotImplementedError()

    def get_auth(self, token):
        raise NotImplementedError()


class MicrosoftOAuth(AbstractOAuth):

    def get_url(self):
        path = "https://login.live.com/oauth20_authorize.srf"
        params = {
            "client_id": self._client_id,
            "callback": self._callback,
            "scope": " ".join(self._scope),
            "response_type": "token"
        }
        return self._format_url(path, params)

    def get_auth(self, token):
        data = {
            "access": token,
            "refresh": ""
        }
        return data


class GoogleOAuth(AbstractOAuth):

    def get_url(self):
        path = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._callback,
            "scope": " ".join(self._scope),
            "response_type": "token",
        }
        return self._format_url(path, params)

    def get_auth(self, token):
        data = {
            "3loauth": token,
        }
        return data
