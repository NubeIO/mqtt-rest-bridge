import enum

import requests
from mrb.setting import BaseSetting
from mrb.validator import is_valid


class MessageType(enum.Enum):
    REQUEST = 'request'
    RESPONSE = 'response'


class HttpMethod(enum.Enum):
    GET = 'GET'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class Request(BaseSetting):
    def __init__(self, api: str = "", body: dict = None, headers: dict = None,
                 http_method: HttpMethod = HttpMethod.GET):
        if body is None:
            body = {}
        self.api: str = api
        self.body: dict = body
        self.headers: dict = headers
        self.http_method: str = http_method.value

    def request(self):
        from mrb.brige import MqttRestBridge

        bridge: MqttRestBridge = MqttRestBridge()
        request_url: str = 'http://0.0.0.0:{}/{}'.format(bridge.port, self.api)
        try:
            resp = requests.request(self.http_method, request_url, json=self.body, headers=self.headers,
                                    params={'bridge': True})
            status: int = resp.status_code
            try:
                content: dict = resp.json() if resp.text else {}
            except ValueError:
                return Response(status=404, error=True, error_message=resp.text)
            error: bool = False
            error_message: str = ''
            if not is_valid(resp):
                error = True
                error_message = content.get('message', '')
                content = {}
            headers = resp.raw.headers.items()
            return Response(content, status, headers, error, error_message)
        except Exception as e:
            return Response(error=True, error_message=str(e))


class Response(BaseSetting):
    def __init__(self, content=None, status: int = 200, headers=None, error: bool = False, error_message=''):
        if content is None:
            content = {}
        self.content: dict = content
        self.status: int = status
        self.headers = headers  # header is not in dictionary form
        self.error: bool = error
        self.error_message: str = error_message
