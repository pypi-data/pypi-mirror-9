import pickle
from event_store.domain.model.event_store_serializer import EventStoreSerializer

__author__ = 'Andriy Drozdyuk'


class PickleSerializer(EventStoreSerializer):
    """Serializes using python's pickle module"""

    def serialize(self, obj):
        return pickle.dumps(obj)

    def deserialize(self, data):
        obj = pickle.loads(data)
        return obj
