import json
import logging
import time
import uuid
from time import sleep
from typing import List

import gevent

from mrb.brige import MqttRestBridge
from mrb.message import Request, Response, MessageType, HttpMethod
from mrb.store import Store, StoreBroadcast, StoreMulticast

logger = logging.getLogger(__name__)


def mqtt_to_rest_mapper(client, userdata, message):
    """topic examples:
    1. master/unicast/<slave_global_uuid>+/<session_uuid>/<req|res>
    2. master/multicast/<slave_global_uuid>+/<session_uuid>
    3. master/broadcast/<slave_global_uuid>+/<session_uuid>
    4. unicast/<slave_global_uuid>/<session_uuid>/<req|res>
    5. multicast/<slave_global_uuid>/<session_uuid>
    6. broadcast/<session_uuid>
    :master                     for directing our request to master
    :unicast                    for one-to-one flow
    :multicast                  for one-to-many flow (master to defined slaves request)
    :broadcast                  for one-to-many flow (master to many slaves & many slaves to master)
    :<slave_global_uuid>        for directing our request to slave device or for giving slave information
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
            slave_global_uuid: str = topic[2]
            session_uuid: str = topic[3]
            response: Response = Response().reload(json.loads(message.payload))
            StoreBroadcast().append(slave_global_uuid, session_uuid, response)
            return
        else:
            slave_global_uuid: str = topic[2]
            session_uuid: str = topic[3]
            response: Response = Response().reload(json.loads(message.payload))
            if topic[1] == 'multicast':
                StoreMulticast().append(slave_global_uuid, session_uuid, response)
                return
            message_type: str = topic[4]
    else:
        if topic[0] == 'broadcast':
            session_uuid: str = topic[1]
            serialize_response: str = request_api(message)
            reply_topic: str = '/'.join(['master', 'broadcast', MqttRestBridge().global_uuid, session_uuid])
            from mrb.mqtt import MqttClient
            MqttClient().publish_value(reply_topic, serialize_response)
            return
        else:
            slave_global_uuid: str = topic[1]
            session_uuid: str = topic[2]
            if topic[0] == 'multicast':
                serialize_response: str = request_api(message)
                reply_topic: str = "/".join(['master', 'multicast', slave_global_uuid, session_uuid])
                logger.debug(f'Reply topic: {reply_topic}')
                from mrb.mqtt import MqttClient
                MqttClient().publish_value(reply_topic, serialize_response)
                return
            message_type: str = topic[3]

    if message_type == MessageType.REQUEST.value:
        serialize_response: str = request_api(message)
        if master:
            reply_topic: str = "/".join(['unicast', slave_global_uuid, session_uuid, MessageType.RESPONSE.value])
        else:
            reply_topic: str = "/".join(
                ['master', 'unicast', slave_global_uuid, session_uuid, MessageType.RESPONSE.value])
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
                              http_method: HttpMethod = HttpMethod.GET, headers: dict = None, timeout: int = 10):
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    topic: str = "/".join(['unicast', slave_global_uuid, session_uuid, MessageType.REQUEST.value])
    publish_request(api, body, headers, http_method, topic)
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


def api_to_slaves_multicast_topic_mapper(slaves_global_uuids: List[str], api: str, body: dict = None,
                                         http_method: HttpMethod = HttpMethod.GET, headers: dict = None,
                                         timeout: int = 10):
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    for slave_global_uuid in slaves_global_uuids:
        topic: str = "/".join(['multicast', slave_global_uuid, session_uuid])
        publish_request(api, body, headers, http_method, topic)
    start_time: float = time.time()
    while True:
        if time.time() - start_time <= timeout:
            sleep(0.01)
            response: Response = StoreMulticast().get(slaves_global_uuids, session_uuid)
            if response:
                return response
        else:
            return Response(error=True,
                            error_message=f'Slaves multicast request timeout, exceed the time {timeout} secs',
                            status_code=408)


def api_to_slaves_broadcast_topic_mapper(api: str, body: dict = None, http_method: HttpMethod = HttpMethod.GET,
                                         headers: dict = None, timeout: int = 10):
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    topic: str = "/".join(['broadcast', session_uuid])
    publish_request(api, body, headers, http_method, topic)
    sleep(timeout)
    response: Response = StoreBroadcast().get(session_uuid)
    if response:
        return response
    else:
        return Response(error=True,
                        error_message=f'Not found exception',
                        status_code=404)


def api_to_master_topic_mapper(api: str, body: dict = None, http_method: HttpMethod = HttpMethod.GET,
                               headers: dict = None, timeout: int = 10):
    mrb: MqttRestBridge = MqttRestBridge()
    api: str = api.strip("/")
    session_uuid: str = __create_uuid()
    topic: str = "/".join(['master', 'unicast', mrb.global_uuid, session_uuid, MessageType.REQUEST.value])
    publish_request(api, body, headers, http_method, topic)
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


def publish_request(api: str, body: dict, headers: dict, http_method: HttpMethod, topic: str):
    logger.debug(f'Request topic: {topic}')
    request: Request = Request(api, body, headers, http_method)
    payload: str = request.serialize()
    logger.debug(f'Request payload: {payload}')
    logger.debug(f'Publishing to MQTT...')
    from mrb.mqtt import MqttClient
    MqttClient().publish_value(topic, payload)


def __create_uuid() -> str:
    return str(uuid.uuid4())
