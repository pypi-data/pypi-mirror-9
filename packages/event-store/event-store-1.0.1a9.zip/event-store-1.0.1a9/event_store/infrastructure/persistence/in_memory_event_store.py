from event_store.domain.model.event_store import EventStore
from event_store.domain.model.exceptions import ConcurrencyProblem
from event_store.domain.model.sequenced_event_store import SequencedEventStore
from event_store.infrastructure.reflection.reflection import obj_name, cls_name
from collections import namedtuple, defaultdict

class Aggregate(object):
    def __init__(self, aggregate_id, aggregate_type, version):
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.version = version
        self.events = []
        
    
Event = namedtuple('Event', ['data', 'version', 'event_type'])
class InMemoryEventStore(EventStore, SequencedEventStore):
    def __init__(self):
        self.aggregates = {}

        # All events appended as they come
        self.all_events = []
        
    def save_changes(self, aggregate_id, aggregate_type, originating_version, events):
        """
        :param str aggregate_type: Fully qualified name of an aggregate, useful for
        error checking purposes.
        """
        aggregate = self.aggregates.get(aggregate_id, None)
        version = 0
        if aggregate is None:
            # Create an aggregate with version 0
            aggregate = Aggregate(aggregate_id=aggregate_id, aggregate_type=aggregate_type, version=version)
            self.aggregates[aggregate_id] = aggregate

        version = aggregate.version
        if originating_version != version:
            raise ConcurrencyProblem()

        # Sanity check - the aggregate id should match its type
        assert (aggregate_type == aggregate.aggregate_type)

        incremented_version = originating_version
        for event in events:
            incremented_version += 1
            # Append event to the aggregate
            aggregate.events.append(Event(data=event, version=incremented_version, event_type=obj_name(event)))
            self.all_events.append(event)

        # Update the aggregate with the last version number
        aggregate.version = incremented_version


    def get_events_by_type(self, event_type, sequence_number=0):
        """
        :param type event_type: Cls of the event to get.
        :param int sequence_number: Get events with sequence_number strictly greater than the given one.
        Sequencing of events starts at 1.
        :rtype: list[Event]
        """
        i = sequence_number + 1
        return [e.data for e in self.all_events[i:] if e.event_type == cls_name(event_type)]


    def get_events_for(self, aggregate_id):
        """Returns events for a given aggregate or None if the aggregate does not exist."""
        aggregate = self.aggregates.get(aggregate_id, None)
        if aggregate is None:
            return None
        else:
            return [event.data for event in aggregate.events]
