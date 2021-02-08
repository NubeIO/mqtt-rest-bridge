# MQTT REST Bridge

MQTT REST Bridge is a package to bridge between MQTT and REST protocols. We call APIs make multiple Python projects
connected with it.

### How to install

```bash
poetry add git+https://github.com/NubeIO/mqtt-rest-bridge@master
```

### How to delete

```bash
poetry remove mqtt-rest-bridge
```

### How to integrate

```bash
MqttRestBridge(port=<int>, identifier=<str>, prod=<True|False>, mqtt_setting=<MqttSetting>)
```


### Request examples

Example to GET:

```python
from mrb.mapper import api_to_topic_mapper
from mrb.message import Response, HttpMethod

response: Response = api_to_topic_mapper(api=f'/api/generic/networks',
                                         destination_identifier=f'ps', http_method=HttpMethod.GET)
```

Example to POST:
```python
import json
from mrb.mapper import api_to_topic_mapper
from mrb.message import Response, HttpMethod

body: json = {
    "name": "generic_network",
    "enable": True,
    "history_enable": True
}
response: Response = api_to_topic_mapper(api=f"/api/generic/networks",
                                         destination_identifier=f'ps',
                                         body=body,
                                         headers={},
                                         http_method=HttpMethod.POST)
```

Example to DELETE:

```python
from mrb.mapper import api_to_topic_mapper
from mrb.message import Response, HttpMethod

response: Response = api_to_topic_mapper(api=f'/api/generic/networks/b7a23aa5-b8a1-4a0f-9acf-4fb011bce50e',
                                         destination_identifier=f'ps', http_method=HttpMethod.DELETE)
```

### Check response is valid or not

```python
from mrb.message import Response
from mrb.validator import is_valid

mapping: Response = Response()
is_valid(mapping)  # returns True of False
```


### How to differentiate REST vs MQTT > REST requests

```
is_bridge(request.args)  # True if MQTT > REST, else REST
```
