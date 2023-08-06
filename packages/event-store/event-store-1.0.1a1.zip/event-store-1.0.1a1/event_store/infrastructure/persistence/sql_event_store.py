from event_store.domain.model.event_store import EventStore
from event_store.domain.model.exceptions import ConcurrencyProblem
from event_store.infrastructure.persistence.schema.event_store_schema import Aggregate, Event


class SqlEventStore(EventStore):
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
            aggregate = Aggregate(aggregate_id=aggregate_id, aggregate_type=aggregate_type, version=0)
            self.session.add(aggregate)

        version = aggregate.version
        if originating_version != version:
            raise ConcurrencyProblem()

        # Sanity check - the aggregate id should match its type
        assert(aggregate_type == aggregate.aggregate_type)

        incremented_version = originating_version
        for event in events:
            incremented_version += 1
            # Append event to the aggregate
            serialized = self.serializer.serialize(event)
            aggregate.events.append(Event(data=serialized, version=incremented_version))

        # Update the aggregate with the last version number
        aggregate.version = incremented_version

    def get_events_for(self, aggregate_id):
        aggregate = self.session.query(Aggregate).get(aggregate_id)
        if aggregate is None:
            return []
        else:
            return [self.serializer.deserialize(event.data) for event in aggregate.events]
