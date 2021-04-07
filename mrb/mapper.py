import json
import logging
import time
import uuid
from time import sleep

import gevent

from mrb.brige import MqttRestBridge
from mrb.message import Request, Response, MessageType, HttpMethod
from mrb.store import Store, StoreBroadcast

logger = logging.getLogger(__name__)


def mqtt_to_rest_mapper(client, userdata, message):
    """topic examples:
    1. slave to master: master/<slave_global_uuid>+/<message_type>/<uuid>
    2. master to slave: <slave_global_uuid>/<message_type>/<uuid>
    :master                     for directing our request to master
    :<slave_global_uuid>        for directing our request to slave device
    :<message_type>             for parsing data whether it's request or response
    :<session_uuid>             for particular request/response cycle
    (there could be multiple request response for same REST request)
    """
    gevent.spawn(_mqtt_to_rest_mapper_process, message)


def _mqtt_to_rest_mapper_process(message):
    master: bool = False
    topic = message.topic.split('/')
    if topic[0] == 'master':
        master = True
        if topic[1] == 'broadcast':
            session_uuid: str = topic[2]
            response: Response = Response().reload(json.loads(message.payload))
            StoreBroadcast().append(session_uuid, response)
            return
        else:
            slave_global_uuid: str = topic[2]
            message_type: str = topic[3]
            session_uuid: str = topic[4]
    else:
        if topic[0] == 'broadcast':
            session_uuid: str = topic[1]
            serialize_response: str = request_api(message)
            reply_topic: str = '/'.join(['master', 'broadcast', session_uuid])
            from mrb.mqtt import MqttClient
            MqttClient().publish_value(reply_topic, serialize_response)
            return
        else:
            slave_global_uuid: str = topic[1]
            message_type: str = topic[2]
            session_uuid: str = topic[3]

    if message_type == MessageType.REQUEST.value:
        serialize_response: str = request_api(message)
        if master:
            reply_topic: str = "/".join(['unicast', slave_global_uuid, MessageType.RESPONSE.value, session_uuid])
        else:
            reply_topic: str = "/".join(
                ['master', 'unicast', slave_global_uuid, MessageType.RESPONSE.value, session_uuid])
        logger.debug(f'Reply topic: {reply_topic}')
        from mrb.mqtt import MqttClient
        MqttClient().publish_value(reply_topic, serialize_response)

    if message_type == MessageType.RESPONSE.value:
        logger.debug(f'Response payload: {message.payload}')
        response: Response = Response().reload(json.loads(message.payload))
        Store().add(session_uuid, response)


def request_api(message) -> str:
    logger.debug(f'Received request payload: {message.payload}')
    request: Request = Request().reload(json.loads(message.payload))
    response: Response = request.request()
    serialize_response: str = response.serialize(pretty=False)
    logger.debug(f'Reply response: {serialize_response}')
    return serialize_response


def api_to_slave_topic_mapper(slave_global_uuid: str, api: str, body: dict = None,
                              http_method: HttpMethod = HttpMethod.GET, headers: dict = None):
    mrb: MqttRestBridge = MqttRestBridge()
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    topic: str = "/".join(['unicast', slave_global_uuid, MessageType.REQUEST.value, session_uuid])
    publish_request(api, body, headers, http_method, topic)
    timeout: int = mrb.mqtt_setting.timeout
    start_time: float = time.time()
    while True:
        if time.time() - start_time <= timeout:
            sleep(0.01)
            response: Response = Store().get(session_uuid)
            if response:
                return response
        else:
            return Response(error=True,
                            error_message=f'Slave {slave_global_uuid} request timeout, exceed the time {timeout} secs',
                            status_code=408)


def api_to_slaves_topic_mapper(api: str, body: dict = None, http_method: HttpMethod = HttpMethod.GET,
                               headers: dict = None):
    mrb: MqttRestBridge = MqttRestBridge()
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    topic: str = "/".join(['broadcast', session_uuid])
    publish_request(api, body, headers, http_method, topic)
    timeout: int = mrb.mqtt_setting.timeout
    sleep(timeout)
    response: Response = StoreBroadcast().get(session_uuid)
    if response:
        return response
    else:
        return Response(error=True,
                        error_message=f'Not found exception',
                        status_code=404)


def api_to_master_topic_mapper(api: str, body: dict = None, http_method: HttpMethod = HttpMethod.GET,
                               headers: dict = None):
    mrb: MqttRestBridge = MqttRestBridge()
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    topic: str = "/".join(['master', 'unicast', mrb.global_uuid, MessageType.REQUEST.value, session_uuid])
    publish_request(api, body, headers, http_method, topic)
    timeout: int = mrb.mqtt_setting.timeout
    start_time: float = time.time()
    while True:
        if time.time() - start_time <= timeout:
            sleep(0.01)
            response: Response = Store().get(session_uuid)
            if response:
                return response
        else:
            return Response(error=True,
                            error_message=f'Master request timeout, exceed the time {timeout} secs',
                            status_code=408)


def publish_request(api, body, headers, http_method, topic):
    logger.debug(f'Request topic: {topic}')
    request: Request = Request(api, body, headers, http_method)
    payload: str = request.serialize()
    logger.debug(f'Request payload: {payload}')
    logger.debug(f'Publishing to MQTT...')
    from mrb.mqtt import MqttClient
    MqttClient().publish_value(topic, payload)


def __create_uuid() -> str:
    return str(uuid.uuid4())
