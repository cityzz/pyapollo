import hmac
import hashlib
import time
import base64
from urllib.parse import urlparse
import requests


class ApolloClient():
    ALGORITHM_NAME = "sha1"
    ENCODING = "utf-8"
    DELIMITER = "\n"

    def __init__(self, config_meta:str, app_id:str,
                 cluster:str, secret:str=None):
        self._config_meta = config_meta
        self._app_id = app_id
        self._cluster = cluster
        self._secret = secret
        self._namespace = None
        self._url = None
        self._cache = {}

    def _gen_url(self):
        return f'{self._config_meta}/configs/{self._app_id}/{self._cluster}/{self._namespace}'

    def _gen_auth_header(self):
        url_sign, timestamp = ApolloClient.get_signature(self._url, self._secret)
        headers = {
            "Authorization": f"Apollo {self._app_id}:{url_sign}",
            "Timestamp": timestamp
        }
        return headers

    @staticmethod
    def sign_string(string_to_sign, access_key_secret):
        try:
            key = access_key_secret.encode(ApolloClient.ENCODING)
            message = string_to_sign.encode(ApolloClient.ENCODING)

            hmac_obj = hmac.new(key, message, hashlib.sha1)
            sign_data = hmac_obj.digest()

            return base64.b64encode(sign_data).decode(ApolloClient.ENCODING)
        except Exception as e:
            raise ValueError(str(e))

    @staticmethod
    def url2path_with_query(url_string):
        try:
            parsed_url = urlparse(url_string)
            path = parsed_url.path
            query = parsed_url.query
            path_with_query = path
            if query:
                path_with_query += "?" + query
            return path_with_query
        except ValueError:
            raise ValueError(f"Invalid url pattern: {url_string}")

    @staticmethod
    def signature(timestamp, path_with_query, secret):
        string_to_sign = timestamp + ApolloClient.DELIMITER + path_with_query
        return ApolloClient.sign_string(string_to_sign, secret)

    @staticmethod
    def get_signature(url, secret):
        timestamp = str(int(time.time() * 1000))
        path_with_query = ApolloClient.url2path_with_query(url)
        return ApolloClient.signature(timestamp, path_with_query, secret), timestamp

    def get_namespace(self, namespace):
        self._namespace = namespace
        self._url = self._gen_url()
        if self._secret is not None:
            self._auth_headers = self._gen_auth_header()

        response = requests.get(self._url, headers=self._auth_headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_value(self, namespace, value):
        namespace_obj = self._cache.get(namespace, None)
        if namespace_obj is None:
            namespace_obj = self.get_namespace(namespace)
            self._cache[namespace] = namespace_obj

        ret = None
        if namespace_obj is not None:
            conf = namespace_obj.get('configurations', None)
            if conf is not None:
                ret = conf.get(value, None)
        return ret

    def get_values(self, namespace):
        namespace_obj = self._cache.get(namespace, None)
        if namespace_obj is None:
            namespace_obj = self.get_namespace(namespace)
            self._cache[namespace] = namespace_obj

        conf = None
        if namespace_obj is not None:
            conf = namespace_obj.get('configurations', None)
        return conf
