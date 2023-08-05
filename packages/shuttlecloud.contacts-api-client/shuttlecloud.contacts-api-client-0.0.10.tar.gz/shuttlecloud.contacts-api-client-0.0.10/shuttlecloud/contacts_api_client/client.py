import time
import json
import hashlib
import requests


class NetworkClient(object):

    def __init__(self, app_id, secret_token):
        self._app_id = app_id
        self._secret_token = secret_token

    def _get_signature(self, timestamp):
        """
        Returns the signature to authenticate the request for the given timestamp.
        """
        signature = "{{{app_id}:{secret_token}:{timestamp}}}".format(
            app_id=self._app_id, secret_token=self._secret_token, timestamp=timestamp)
        signature = hashlib.sha256(signature).hexdigest()
        return signature

    def _get_auth_params(self):
        """
        Returns the dictionary with the authentication parameters (sig, appid, ts).
        """
        timestamp = int(time.time())
        data = {
            "sig": self._get_signature(timestamp),
            "appid": self._app_id,
            "ts": timestamp
        }
        return data

    def request(self, method, url, data=None, auth_required=True, serializer=json.dumps, **kwargs):
        """
        Makes a HTTP request with the given method, url and data.
        Returns a response as a tuple (status_code, data)
        """
        if method in ("head", "get"):
            kwargs.setdefault("allow_redirects", True)
        if data:
            if serializer:
                data = serializer(data)
            kwargs["data"] = data
        if auth_required:
            kwargs["params"] = self._get_auth_params()

        response = requests.request(method, url, **kwargs)
        response_status = response.status_code
        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text.strip()

        return response_status, response_data


class ContactsApi(object):

    BASIC_AUTHENTICATION = "basic"
    OAUTH_AUTHENTICATION = "oauth"

    JOB_STARTED = "STARTED"
    JOB_COMPLETED = "COMPLETED"
    JOB_PENDING = "PENDING_AUTHENTICATION"
    JOB_REVIEW = "REVIEW"

    def __init__(self, api_url, app_id, secret_token):
        self._api_url = api_url.rstrip("/")
        self._api_client = NetworkClient(app_id, secret_token)

    def capabilities(self, email):
        """
        Verifies whether the email provider is supported.
        """
        method = "POST"
        url = "{base}/auth/capabilities".format(base=self._api_url)
        data = {
            "userid": {
                "email": email,
            },
        }
        response = self._api_client.request(method, url, data)
        return response

    def load(self, email, auth_token):
        """
        Loads a job for extracting contacts from the given email account.
        """
        method = "POST"
        url = "{base}/load".format(base=self._api_url)
        data = {
            "contactsextraction": {
                "sourceaccount": {
                    "userid": {
                        "email": email,
                    },
                    "auth": auth_token,
                }
            }
        }
        response = self._api_client.request(method, url, data)
        return response

    def status(self, job_id):
        """
        Checks the status for the given job_id.
        """
        method = "GET"
        url = "{base}/status/{job_id}".format(base=self._api_url, job_id=job_id)

        response = self._api_client.request(method, url)
        return response

    def contacts(self, operation_id):
        """
        Fetches a chunk of vcards for the given operation_id.
        """
        method = "GET"
        url = "{base}/contacts/{operation_id}".format(base=self._api_url, operation_id=operation_id)

        response = self._api_client.request(method, url)
        return response
