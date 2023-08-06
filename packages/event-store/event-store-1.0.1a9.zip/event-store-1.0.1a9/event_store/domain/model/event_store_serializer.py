__author__ = 'Andriy Drozdyuk'
from abc import ABCMeta, abstractmethod


class EventStoreSerializer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def serialize(self, obj):
        """Serialize a given object"""
        pass

    @abstractmethod
    def deserialize(self, data):
        """De-serialize data back into an object"""
        pass
