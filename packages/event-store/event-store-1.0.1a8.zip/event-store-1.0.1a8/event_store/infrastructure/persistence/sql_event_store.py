from event_store.domain.model.event_store import EventStore
from event_store.domain.model.exceptions import ConcurrencyProblem
from event_store.domain.model.sequenced_event_store import SequencedEventStore
from event_store.infrastructure.persistence.schema.event_store_schema import Aggregate, Event
from event_store.infrastructure.reflection.reflection import obj_name, cls_name


class SqlEventStore(EventStore, SequencedEventStore):
    def __init__(self, session, serializer):
        """
        :param session: SqlAlchemy session object
        :param EventStoreSerializer serializer: Serializer to use
        """
        self.session = session
        self.serializer = serializer

    def save_changes(self, aggregate_id, aggregate_type, originating_version, events):
        """
        :param str aggregate_type: Fully qualified name of an aggregate, useful for
        error checking purposes.
        """

        aggregate = self.session.query(Aggregate).get(aggregate_id)
        version = 0
        if aggregate is None:
            # Create an aggregate with version 0
            aggregate = Aggregate(aggregate_id=aggregate_id, aggregate_type=aggregate_type, version=version)
            self.session.add(aggregate)

        version = aggregate.version
        if originating_version != version:
            raise ConcurrencyProblem()

        # Sanity check - the aggregate id should match its type
        assert (aggregate_type == aggregate.aggregate_type)

        incremented_version = originating_version
        for event in events:
            incremented_version += 1
            # Append event to the aggregate
            serialized = self.serializer.serialize(event)
            aggregate.events.append(Event(data=serialized, version=incremented_version, event_type=obj_name(event)))

        # Update the aggregate with the last version number
        aggregate.version = incremented_version

    def get_events_by_type(self, event_type, sequence_number=0):
        """
        :param type event_type: Cls of the event to get.
        :param int sequence_number: Get events with sequence_number strictly greater than the given one.
        Sequencing of events starts at 1.
        :rtype: list[Event]
        """
        print("Trying to get events of type: %s, with seq_num > %s" % (cls_name(event_type), sequence_number))
        events = self.session.query(Event).filter(Event.event_type == cls_name(event_type)).filter(
            Event.sequence_number > sequence_number)
        return [self.serializer.deserialize(event.data) for event in events]

    def get_events_for(self, aggregate_id):
        aggregate = self.session.query(Aggregate).get(aggregate_id)
        if aggregate is None:
            return []
        else:
            return [self.serializer.deserialize(event.data) for event in aggregate.events]
