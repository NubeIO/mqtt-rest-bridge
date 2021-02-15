import logging
import time
from typing import Callable

import paho.mqtt.client as mqtt

from mrb.mapper import mqtt_to_rest_mapper
from mrb.setting import MqttSetting
from mrb.utils.singleton import Singleton

logger = logging.getLogger(__name__)


class MqttClient(metaclass=Singleton):

    def __init__(self):
        self.__config: MqttSetting = None
        self.__client: mqtt.Client = None
        self.__subscribe_topic: str = None

    @property
    def config(self) -> MqttSetting:
        return self.__config

    def start(self, config: MqttSetting, subscribe_topic: str, callback: Callable):
        self.__config = config
        self.__subscribe_topic = subscribe_topic
        logger.info(f'Starting MQTT client[{self.config.name}]...')
        self.__client = mqtt.Client(self.config.name)
        if self.config.authentication:
            self.__client.username_pw_set(self.config.username, self.config.password)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = mqtt_to_rest_mapper
        if self.config.attempt_reconnect_on_unavailable:
            while True:
                try:
                    self.__client.connect(self.config.host, self.config.port, self.config.keepalive)
                    break
                except (ConnectionRefusedError, OSError) as e:
                    logger.error(
                        f'MQTT client[{self.config.name}] connection failure {self.to_string()} -> '
                        f'{type(e).__name__}. Attempting reconnect in '
                        f'{self.config.attempt_reconnect_secs} seconds')
                    time.sleep(self.config.attempt_reconnect_secs)
        else:
            try:
                self.__client.connect(self.config.host, self.config.port, self.config.keepalive)
            except Exception as e:
                # catching so can set __client to None so publish_cov doesn't stack messages forever
                self.__client = None
                logger.error(str(e))
                return
        logger.info(f'MQTT client {self.config.name} connected {self.to_string()}')
        if callback:
            callback()
        self.__client.loop_forever()

    def status(self) -> bool:
        return bool(self.config and self.config.enabled and self.__client and self.__client.is_connected())

    def to_string(self) -> str:
        return f'{self.config.host}:{self.config.port}'

    def __on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code > 0:
            reasons = {
                1: 'Connection refused - incorrect protocol version',
                2: 'Connection refused - invalid client identifier',
                3: 'Connection refused - server unavailable',
                4: 'Connection refused - bad username or password',
                5: 'Connection refused - not authorised'
            }
            reason = reasons.get(reason_code, 'unknown')
            self.__client = None
            raise Exception(f'MQTT Connection Failure: {reason}')
        self.__on_connection_successful()

    def __on_connection_successful(self):
        logger.debug(f'MQTT sub to {self.__subscribe_topic}')
        self.__client.subscribe(self.__subscribe_topic)

    def publish_value(self, topic: str, payload: str):
        if not self.__config:
            return
        timeout: int = self.__config.timeout
        start_time: float = time.time()
        while True:
            if self.status():
                self.__client.publish(topic, payload, self.config.qos)
                return
            else:
                if time.time() - start_time <= timeout:
                    time.sleep(0.01)
                else:
                    logger.error(f'Failed to publish value: {payload}, on topic: {topic}')
                    return
