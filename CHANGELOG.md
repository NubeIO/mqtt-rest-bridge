# CHANGELOG
## [v1.8.2](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.8.2) (2022-04-19)
- Upgrade rubix-registry version to v1.2.0

## [v1.8.1](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.8.1) (2022-04-08)
- Improvement: Too many open files

## [v1.8.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.8.0) (2022-01-21)
- Upgrade rubix-mqtt to v1.3.0

## [v1.7.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.7.0) (2020-11-11)
- Upgrade rubix-registry

## [v1.6.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.6.0) (2020-08-01)
- Response back even when all multicast doesn't response

## [v1.5.1](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.5.1) (2020-06-21)
- rubix-registry upgrade for get/put issue fix

## [v1.5.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.5.0) (2020-06-14)
- rubix-registry upgrade for global_uuid

## [v1.4.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.4.0) (2020-05-31)
- Support multiple Content-Types for upload/download

## [v1.3.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.3.0) (2020-05-03)
- Timeout param support for MQTT > REST request

## [v1.2.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.2.0) (2020-04-05)
- Master <> Slave request/response change
- Support broadcast and collect messages from slave
- Use rubix-registry global_uuid (we were creating on this project itself)
- Upgrade rubix-mqtt version (async MQTT connection)
- Broadcast response change (wrap under guuid)
- Multicast request support (collect data from multicasted slaves)

## [v1.1.4](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.1.4) (2020-03-10)
- Make retain false
- Upgrade rubix-mqtt version

## [v1.1.3](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.1.3) (2020-02-03)
- MQTT message listener issue fix

## [v1.1.2](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.1.2) (2020-02-23)
- Use rubix-mqtt base
- Add a test case

## [v1.1.1](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.1.1) (2020-02-15)
- Don't try to publish value if MQTT is not setup

## [v1.1.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.1.0) (2020-02-14)
- Improvement on existing codes
- Added callback function
- Response class attributes change

## [v1.0.0](https://github.com/NubeIO/mqtt-rest-bridge/tree/v1.0.0) (2020-02-09)
- First initial release for MQTT REST communication
