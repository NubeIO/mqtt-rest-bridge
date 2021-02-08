import json
import logging
import time
import uuid
from threading import Thread
from time import sleep

from mrb.brige import MqttRestBridge
from mrb.message import Request, Response, MessageType, HttpMethod
from mrb.store import Store

logger = logging.getLogger(__name__)


def mqtt_to_rest_mapper(client, userdata, message):
    """topic example            <global_uuid>/<destination_identifier>/<source_identifier>/<message_type>/<uuid>
    :<global_uuid>              for restricting message on local system (same device)
    :<destination_identifier>   for where MQTT data is to travel
    :<source_identifier>        for from where MQTT data is travelling (to response back)
    :<message_type>             for parsing data whether it's request or response
    :<session_uuid>             for particular request/response cycle
    (there could be multiple request response for same REST request)
    """
    Thread(target=_mqtt_to_rest_mapper, kwargs={'message': message}).start()


def _mqtt_to_rest_mapper(message):
    topic = message.topic.split('/')
    if len(topic) != 5:
        return
    global_uuid: str = topic[0]
    destination: str = topic[1]
    source: str = topic[2]
    message_type: str = topic[3]
    session_uuid: str = topic[4]

    if message_type == MessageType.REQUEST.value:
        logger.debug(f'received request payload: {message.payload}')
        request: Request = Request().reload(json.loads(message.payload))
        response: Response = request.request()
        serialize_response: str = response.serialize(pretty=False)
        logger.debug(f'reply response: {serialize_response}')
        reply_topic: str = "/".join([global_uuid, source, destination, MessageType.RESPONSE.value, session_uuid])
        logger.debug(f'reply topic: {reply_topic}')
        from mrb.mqtt import MqttClient
        MqttClient().publish_value(reply_topic, serialize_response)

    if message_type == MessageType.RESPONSE.value:
        logger.debug(f'response payload: {message.payload}')
        response: Response = Response().reload(json.loads(message.payload))
        Store().add(session_uuid, response)


def api_to_topic_mapper(api: str, destination_identifier: str, body: dict = None, headers: dict = None,
                        http_method: HttpMethod = HttpMethod.GET) -> Response:
    mrb: MqttRestBridge = MqttRestBridge()
    source: str = mrb.identifier
    global_uuid: str = mrb.global_uuid
    session_uuid: str = __create_uuid()
    topic: str = "/".join([global_uuid, destination_identifier, source, MessageType.REQUEST.value, session_uuid])
    logger.debug(f'request topic: {topic}')
    request: Request = Request(api, body, headers, http_method)
    payload: str = request.serialize()
    logger.debug(f'request payload: {payload}')
    logger.debug(f'publishing to MQTT...')
    from mrb.mqtt import MqttClient
    MqttClient().publish_value(topic, payload)

    timeout: int = mrb.mqtt_setting.timeout
    start_time: float = time.time()
    while True:
        if time.time() - start_time <= timeout:
            sleep(0.01)
            response: Response = Store().get(session_uuid)
            if response:
                return response
        else:
            return Response(error=True, message=f'timeout, exceed the time {timeout} sec')


def __create_uuid() -> str:
    return str(uuid.uuid4())
