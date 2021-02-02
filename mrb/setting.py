import json
import os
import uuid
from abc import ABC

from mrb.utils.file import read_file, write_file
from mrb.utils.singleton import Singleton


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
        self.retain = False
        self.attempt_reconnect_on_unavailable = True
        self.attempt_reconnect_secs = 5


class MqttRestBridgeSetting(metaclass=Singleton):
    default_global_uuid_file = 'global_uuid.txt'

    def __init__(self, **kwargs):
        self.__prod: bool = kwargs.get('prod') or False
        self.__mqtt_setting: MqttSetting = MqttSetting()
        self.__data_dir = None
        self.__global_uuid: str = 'local'
        self.__identifier: str = 'identifier'
        if self.__prod:
            self.__data_dir = self.__compute_dir(kwargs.get('data_dir'))
            self.__global_uuid_file = os.path.join(self.data_dir, self.default_global_uuid_file)
            self.__global_uuid = self.__handle_global_uuid(self.global_uuid_file)

    @property
    def data_dir(self):
        return self.__data_dir

    @property
    def prod(self) -> bool:
        return self.__prod

    @property
    def mqtt(self) -> MqttSetting:
        return self.__mqtt_setting

    @property
    def global_uuid_file(self) -> str:
        return self.__global_uuid_file

    @property
    def global_uuid(self) -> str:
        return self.__global_uuid

    @property
    def identifier(self) -> str:
        return self.__identifier

    def serialize(self, pretty=True) -> str:
        m = {MqttSetting.KEY: self.mqtt, 'prod': self.prod, 'data_dir': self.data_dir, 'global_uuid': self.global_uuid}
        return json.dumps(m, default=lambda o: o.to_dict() if isinstance(o, BaseSetting) else o.__dict__,
                          indent=2 if pretty else None)

    def reload(self, setting: dict):
        self.__mqtt_setting = self.__mqtt_setting.reload(setting)
        return self

    @staticmethod
    def __compute_dir(_dir: str, mode=0o744) -> str:
        d = _dir if os.path.isabs(_dir) else os.path.join(os.getcwd(), _dir)
        os.makedirs(d, mode, True)
        return d

    @staticmethod
    def __handle_global_uuid(global_uuid_file) -> str:
        if MqttRestBridgeSetting.prod:
            existing_secret_key = read_file(global_uuid_file)
            if existing_secret_key.strip():
                return existing_secret_key

            global_uuid = MqttRestBridgeSetting.__create_global_uuid()
            write_file(global_uuid_file, global_uuid)
            return global_uuid
        return ''

    @staticmethod
    def __create_global_uuid() -> str:
        return str(uuid.uuid4())
