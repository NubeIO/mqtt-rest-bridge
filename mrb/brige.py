import json
import os
import uuid

from mrb.setting import MqttSetting, BaseSetting
from mrb.utils.file import read_file, write_file
from mrb.utils.singleton import Singleton


class MqttRestBridge(metaclass=Singleton):
    default_global_uuid_file = 'global_uuid.txt'

    def __init__(self, **kwargs):
        self.__port: int = kwargs.get('port') or 8080
        self.__identifier: str = kwargs.get('identifier') or 'identifier'
        self.__prod: bool = kwargs.get('prod') or False
        self.__mqtt_setting = None
        self.__data_dir = None
        self.__global_uuid: str = 'local'
        if self.__prod:
            self.__data_dir = self.__compute_dir(kwargs.get('data_dir') or '/data/mqtt-rest-bridge')
            self.__global_uuid_file = os.path.join(self.data_dir, self.default_global_uuid_file)
            self.__global_uuid = self.__handle_global_uuid(self.global_uuid_file)

    @property
    def data_dir(self):
        return self.__data_dir

    @property
    def prod(self) -> bool:
        return self.__prod

    @property
    def mqtt_setting(self) -> MqttSetting:
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

    @property
    def port(self) -> int:
        return self.__port

    def serialize(self, pretty=True) -> str:
        m = {
            MqttSetting.KEY: self.mqtt_setting,
            'prod': self.prod,
            'data_dir': self.data_dir,
            'global_uuid': self.global_uuid
        }
        return json.dumps(m, default=lambda o: o.to_dict() if isinstance(o, BaseSetting) else o.__dict__,
                          indent=2 if pretty else None)

    def reload_mqtt(self, mqtt_setting: MqttSetting):
        self.__mqtt_setting = mqtt_setting
        from mrb.mqtt import MqttClient
        mqtt_client = MqttClient()
        mqtt_client.start(self.__mqtt_setting, f'{self.global_uuid}/{self.identifier}/#')
        return self

    @staticmethod
    def __compute_dir(_dir: str, mode=0o744) -> str:
        d = _dir if os.path.isabs(_dir) else os.path.join(os.getcwd(), _dir)
        os.makedirs(d, mode, True)
        return d

    @staticmethod
    def __handle_global_uuid(global_uuid_file) -> str:
        if MqttRestBridge.prod:
            existing_secret_key = read_file(global_uuid_file)
            if existing_secret_key.strip():
                return existing_secret_key

            global_uuid = MqttRestBridge.__create_global_uuid()
            write_file(global_uuid_file, global_uuid)
            return global_uuid
        return ''

    @staticmethod
    def __create_global_uuid() -> str:
        return str(uuid.uuid4())
