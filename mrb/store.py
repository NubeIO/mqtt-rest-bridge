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

    def add(self, uuid, response: Response):
        self.__responses[uuid] = response


class StoreBroadcast(metaclass=Singleton):
    def __init__(self):
        self.__responses: {[str]: List[Response]} = {}

    def get(self, uuid: str) -> Union[Response, None]:
        responses: List[Response] = self.__responses.get(uuid)
        response_return = Response(content=[])
        if responses:
            del self.__responses[uuid]
            for response in responses:
                if not response.error:
                    response_return.content.append(response.content)
            return response_return
        return None

    def append(self, uuid, response: Response):
        if not self.__responses.get(uuid):
            self.__responses[uuid] = [response]
        else:
            self.__responses[uuid].append(response)
