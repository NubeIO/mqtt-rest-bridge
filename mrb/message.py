import enum

import requests
from rubix_mqtt.setting import BaseSetting


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
            content_type: str = self.headers.get('Content-Type', '') if self.headers else ""
            if 'multipart/form-data' in content_type:
                return Response(error=True,
                                status_code=501,
                                error_message=str("We don't have the multipart/form-data support yet!"))
            else:
                resp = requests.request(self.http_method,
                                        request_url,
                                        json=self.body,
                                        headers=self.headers,
                                        params={'bridge': True})
            status_code: int = resp.status_code
            if resp.headers['Content-Type'] == "application/json":
                content = resp.json() if resp.text else {}
            else:
                content = resp.text
            error: bool = False
            error_message: str = ''
            if status_code not in range(200, 300):
                error = True
                error_message = content.get('message', '') if isinstance(content, dict) else content
                headers = resp.raw.headers.items()
                headers.append(["Content-Type", "application/json"])
                return Response(status_code=status_code, headers=headers, error=error, error_message=error_message)
            else:
                headers = resp.raw.headers.items()
                return Response(content, status_code, headers, resp.headers.get('content-type'), error, error_message)
        except Exception as e:
            return Response(error=True, error_message=str(e))


class Response(BaseSetting):
    def __init__(self, content=None, status_code: int = 200, headers=None, content_type='application/json',
                 error: bool = False, error_message=''):
        self.content = content or {}
        self.status_code: int = status_code
        self.headers = headers or [["Content-Type", "application/json"]]
        self.content_type: str = content_type
        self.error: bool = error
        self.error_message: str = error_message
