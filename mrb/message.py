import enum
import json

import requests
from mrb.setting import BaseSetting


class HttpMethod(enum.Enum):
    GET = 'GET'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class Request(BaseSetting):
    def __init__(self, url: str, body: json, headers=None, http_method: HttpMethod = HttpMethod.GET):
        self.url: str = url
        self.body: json = body
        self.headers = headers
        self.http_method: HttpMethod = http_method

    def request(self):
        from mrb.brige import MqttRestBridge

        bridge: MqttRestBridge = MqttRestBridge()
        request_url: str = 'http://0.0.0.0:{}/{}'.format(bridge.port, self.url)
        try:
            resp = requests.request(self.http_method.value, request_url, json=self.body, headers=self.headers)
            content: str = str(resp.content)
            status: int = resp.status_code
            headers = resp.raw.headers.items()
            return Response(content, status, headers)
        except ConnectionError:
            pass


class Response(BaseSetting):
    def __init__(self, content: str, status: int, headers=None):
        self.content: str = content
        self.status: int = status
        self.headers = headers
