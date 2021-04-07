import json
import os
import uuid
from typing import Callable, List

from rubix_mqtt.setting import BaseSetting

from mrb.setting import MqttSetting
from mrb.utils.file import read_file, write_file
from mrb.utils.singleton import Singleton


class MqttRestBridge(metaclass=Singleton):
    default_global_uuid_file: str = 'global_uuid.txt'
    out: str = '/data/mqtt-rest-bridge'

    def __init__(self, port: int = 8080, mqtt_setting: MqttSetting = MqttSetting(), data_dir: str = None,
                 callback: Callable = None):
        self.__port: int = port
        self.__mqtt_setting: MqttSetting = mqtt_setting
        self.__mqtt_setting.retain = False
        self.__data_dir = None
        self.__global_uuid: str = 'local'
        self.__callback: Callable = callback
        self.__data_dir = self.__compute_dir(data_dir or MqttRestBridge.out)
        self.__global_uuid_file = os.path.join(self.data_dir, self.default_global_uuid_file)
        self.__global_uuid = self.__handle_global_uuid(self.global_uuid_file)

    @property
    def data_dir(self):
        return self.__data_dir

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
    def port(self) -> int:
        return self.__port

    def serialize(self, pretty=True) -> str:
        m = {
            MqttSetting.KEY: self.mqtt_setting,
            'data_dir': self.data_dir,
            'global_uuid': self.global_uuid
        }
        return json.dumps(m, default=lambda o: o.to_dict() if isinstance(o, BaseSetting) else o.__dict__,
                          indent=2 if pretty else None)

    def start(self):
        from mrb.mqtt import MqttClient
        mqtt_client = MqttClient()
        subscribe_topics: List[str] = []
        if self.mqtt_setting.master:
            subscribe_topics.append(f'master/unicast/+/#')
            subscribe_topics.append(f'master/broadcast/#')
        subscribe_topics.append(f'unicast/{self.global_uuid}/#')
        subscribe_topics.append(f'broadcast/#')
        mqtt_client.start(self.__mqtt_setting, subscribe_topics, self.__callback)
        return self

    @staticmethod
    def status():
        from mrb.mqtt import MqttClient
        return MqttClient().status()

    @staticmethod
    def __compute_dir(_dir: str, mode=0o744) -> str:
        d = _dir if os.path.isabs(_dir) else os.path.join(os.getcwd(), _dir)
        os.makedirs(d, mode, True)
        return d

    @staticmethod
    def __handle_global_uuid(global_uuid_file) -> str:
        existing_secret_key = read_file(global_uuid_file)
        if existing_secret_key.strip():
            return existing_secret_key

        global_uuid = MqttRestBridge.__create_global_uuid()
        write_file(global_uuid_file, global_uuid)
        return global_uuid

    @staticmethod
    def __create_global_uuid() -> str:
        return str(uuid.uuid4())
