
from abc import abstractmethod

class Database(object):

    @abstractmethod
    def get_engine(self):
        pass

    @abstractmethod
    def create_session(self):
        pass
