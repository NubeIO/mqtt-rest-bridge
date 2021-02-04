from mrb.message import Response
from mrb.utils.singleton import Singleton


class Store(metaclass=Singleton):
    def __init__(self):
        self.__responses = {}

    def get(self, uuid: str):
        response: Response = self.__responses.get(uuid)
        if response:
            del self.__responses[uuid]
            return response
        return None

    def add(self, uuid, response: Response):
        self.__responses[uuid] = response
