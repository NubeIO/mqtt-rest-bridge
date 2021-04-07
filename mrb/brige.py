import json
import os
from typing import Callable, List

from registry.registry import RubixRegistry
from rubix_mqtt.setting import BaseSetting

from mrb.setting import MqttSetting
from mrb.utils.singleton import Singleton


class MqttRestBridge(metaclass=Singleton):

    def __init__(self, port: int = 8080, mqtt_setting: MqttSetting = MqttSetting(), callback: Callable = None):
        self.__port: int = port
        self.__mqtt_setting: MqttSetting = mqtt_setting
        self.__mqtt_setting.retain = False
        self.__data_dir = None
        self.__callback: Callable = callback

    @property
    def mqtt_setting(self) -> MqttSetting:
        return self.__mqtt_setting

    @property
    def global_uuid(self) -> str:
        return RubixRegistry().read_wires_plat().get('global_uuid')

    @property
    def port(self) -> int:
        return self.__port

    def serialize(self, pretty=True) -> str:
        m = {MqttSetting.KEY: self.mqtt_setting}
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
