import threading

from mrb.message import Response
from mrb.utils.singleton import Singleton

lock = threading.Lock()


class Store(metaclass=Singleton):
    def __init__(self):
        self.__responses = {}

    def get(self, uuid: str):
        with lock:
            response: Response = self.__responses.get(uuid)
            if response:
                del self.__responses[uuid]
                return response
            return None

    def add(self, uuid, response: Response):
        with lock:
            self.__responses[uuid] = response
