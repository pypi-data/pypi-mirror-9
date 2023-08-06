from abc import abstractmethod, ABCMeta

__author__ = 'Andriy Drozdyuk'


class SequencedEventStore(object):
    """
    Mixin that adds a sequence number to each even in the event_store.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_events_by_type(self, event_type, sequence_number=0):
        """
        Retrieve all events of the given type, with sequence number strictly greater than the given one.

        :param type event_type: Class of the event to get.
        :param int sequence_number: Get events with sequence_number strictly greater than the given one. Sequencing of events starts at 1.
        :returns: Ordered list of events with sequence number strictly greater than `sequence_number` of type `event_type`.
        :rtype: list[object]
        """
        pass