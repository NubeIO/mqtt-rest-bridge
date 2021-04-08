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


class StoreBroadcast(metaclass=Singleton):
    def __init__(self):
        self.__responses: {[str]: List[Response]} = {}

    def get(self, uuid: str) -> Union[Response, None]:
        response: Response = self.__responses.get(uuid)
        if response:
            del self.__responses[uuid]
            return response
        return None

    def append(self, slave_global_uuid: str, uuid: str, response: Response):
        if response.error:
            return
        if self.__responses.get(uuid):
            self.__responses[uuid].content[slave_global_uuid] = response.content
        else:
            self.__responses[uuid] = Response()
            self.__responses[uuid].content[slave_global_uuid] = response.content
