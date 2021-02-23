from mrb.brige import MqttRestBridge
from mrb.setting import MqttSetting


def callback():
    print('callback...')


if __name__ == '__main__':
    bridge = MqttRestBridge(port=8080, identifier=f'identifier', prod=True, mqtt_setting=MqttSetting(),
                            callback=callback)
    bridge.start(False)
