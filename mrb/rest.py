import json
import logging

from mrb.message import Request, Response
from mrb.store import Store

logger = logging.getLogger(__name__)


def mqtt_to_rest_mapper(client, userdata, message):
    """topic example            <global_uuid>/<destination_identifier>/<source_identifier>/<message_type>/<uuid>
    :<global_uuid>              for restricting message on local system (same device)
    :<destination_identifier>   for where MQTT data is to travel
    :<source_identifier>        for from where MQTT data is travelling (to response back)
    :<message_type>             for parsing data whether it's request or response
    :<uuid>                     for particular request/response cycle
    (there could be multiple request response for same REST request)
    """
    topic = message.topic.split('/')
    if len(topic) != 5:
        return
    global_uuid: str = topic[0]
    destination: str = topic[1]
    source: str = topic[2]
    message_type: str = topic[3]
    uuid: str = topic[4]

    if message_type == 'request':
        logger.debug(f'request payload: {message.payload}')
        response: Response = Request('', None).reload(json.loads(message.payload)).request()
        serialize_response: str = response.serialize(pretty=False)
        logger.debug(f'reply response: {serialize_response}')
        # todo need to swap destination & source
        reply_topic: str = "/".join([global_uuid, destination, source, 'response', uuid])
        logger.debug(f'reply topic: {reply_topic}')
        from mrb.mqtt import MqttClient
        MqttClient().publish_value(reply_topic, serialize_response)

    if message_type == 'response':
        logger.debug(f'response payload: {message.payload}')
        response: Response = Response('', 200).reload(json.loads(message.payload))
        Store().add(uuid, response)
