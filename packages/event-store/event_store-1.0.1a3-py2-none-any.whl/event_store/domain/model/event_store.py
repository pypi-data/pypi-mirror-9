from abc import ABCMeta, abstractmethod
from uuid import UUID


class EventStore(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_changes(self, aggregate_id, aggregate_type, originating_version, events):
        """
        :param UUID aggregate_id: Aggregate for which to save the events
        :param str aggregate_type: Fully qualified name of the aggregate.
        :param int originating_version: Version of the last event seen before these changes
        :param list[Event]: Collection of events to persist.
        :raises ConcurrencyProblem: If optimistic lock failed (originating_version did not match expected version).
        """
        pass

    @abstractmethod
    def get_events_for(self, aggregate_id):
        """
        :param UUID aggregate_id: Retrieve all the events for a given aggregate, 
        ordered by incrementing version number.
        :rtype: list[Event]
        """
        pass