from typing import List, Union

from mrb.message import Response
from mrb.utils.singleton import Singleton


class Store(metaclass=Singleton):
    def __init__(self):
        self.__responses: {[str]: Response} = {}

    def get(self, uuid: str) -> Union[Response, None]:
        response: Response = self.__responses.get(uuid)
        if response:
            del self.__responses[uuid]
            return response
        return None

    def add(self, uuid: str, response: Response):
        self.__responses[uuid] = response


class Multicast:
    def __init__(self):
        self.response: Response = Response()
        self.slaves_global_uuids: List[str] = []


class StoreMulticast(metaclass=Singleton):

    def __init__(self):
        self.__responses: {[str]: Multicast} = {}

    def get(self, slaves_global_uuids: List[str], uuid: str, force=False, message=None) -> Union[Response, None]:
        response: {[str]: Multicast} = self.__responses.get(uuid)
        if response:
            if len(response.slaves_global_uuids) == len(slaves_global_uuids):
                del self.__responses[uuid]
                return response.response
            if force:
                for slave_global_uuid in slaves_global_uuids:
                    if slave_global_uuid not in response.slaves_global_uuids:
                        self.__responses[uuid].response.content[slave_global_uuid] = {
                            'error': True,
                            'data': 'Timeout' if not message else message
                        }
                return response.response
        return None

    def append(self, slave_global_uuid: str, uuid: str, response: Response):
        if not self.__responses.get(uuid):
            self.__responses[uuid] = Multicast()
        self.__responses[uuid].slaves_global_uuids.append(slave_global_uuid)
        if response.error:
            return
        self.__responses[uuid].response.content[slave_global_uuid] = {
            'error': False,
            'data': response.content
        }


class StoreBroadcast(metaclass=Singleton):
    def __init__(self):
        self.__responses: {[str]: Response} = {}

    def get(self, uuid: str) -> Union[Response, None]:
        response: Response = self.__responses.get(uuid)
        if response:
            del self.__responses[uuid]
            return response
        return None

    def append(self, slave_global_uuid: str, uuid: str, response: Response):
        if not self.__responses.get(uuid):
            self.__responses[uuid] = Response()
        if response.error:
            return
        self.__responses[uuid].content[slave_global_uuid] = response.content
