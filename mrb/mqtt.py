import logging
import time

from rubix_mqtt.mqtt import MqttClientBase

from mrb.utils.singleton import Singleton

logger = logging.getLogger(__name__)


class MqttClient(MqttClientBase, metaclass=Singleton):

    def __init__(self):
        super().__init__()

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
