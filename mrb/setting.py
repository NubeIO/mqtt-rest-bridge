from rubix_mqtt.setting import MqttSettingBase


class MqttSetting(MqttSettingBase):
    KEY = 'mqtt_rest_bridge'

    def __init__(self):
        super().__init__()
        self.master = False
        self.name = 'mqtt-rest-bridge'
