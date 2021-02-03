import json
from abc import ABC


class BaseSetting(ABC):

    def reload(self, setting: dict):
        if setting is not None:
            self.__dict__ = {k: setting.get(k, v) for k, v in self.__dict__.items()}
        return self

    def serialize(self, pretty=True) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=2 if pretty else None)

    def to_dict(self):
        return json.loads(self.serialize(pretty=False))


class MqttSetting(BaseSetting):
    KEY = 'mqtt_rest_bridge'

    def __init__(self):
        self.enabled = True
        self.name = 'mqtt-rest-bridge'
        self.host = '0.0.0.0'
        self.port = 1883
        self.authentication = False
        self.username = 'username'
        self.password = 'password'
        self.keepalive = 60
        self.qos = 1
        self.attempt_reconnect_on_unavailable = True
        self.attempt_reconnect_secs = 5
