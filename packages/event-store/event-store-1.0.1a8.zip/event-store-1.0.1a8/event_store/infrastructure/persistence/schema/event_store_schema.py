from custom_types import GUID
from sqlalchemy.types import Integer, LargeBinary, String
from sqlalchemy import UniqueConstraint, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class Event(Base):
    __tablename__ = 'event_log'

    # Aggregate to which this event relates
    aggregate_id = Column(String, ForeignKey('aggregates.aggregate_id'),
                          nullable=False)
    # Data for this event
    data = Column(LargeBinary)
    
    # Version of the event, starts at one.
    version = Column(Integer, nullable=False)

    # Sequence number of the event, starts at one.
    # Sequence number is a unique number for an event that is always incrementing.
    sequence_number = Column(Integer, primary_key=True)

    # The name of the event type
    event_type = Column(String(length=300), nullable=False)

    # Provide easy access to aggregate, and the events ordered by version on that aggregate
    aggregate = relationship('Aggregate', backref=backref('events', order_by=version))

    # Version must be unique per aggregate-type
    __table_args__ = (UniqueConstraint('aggregate_id', 'version'),)
                      

class Aggregate(Base):
    __tablename__ = 'aggregates'
    
    aggregate_id = Column(String, primary_key=True)
    # Fully qualified name of the aggregate    
    aggregate_type = Column(String(length=300), unique=True, nullable=False)
    
    # Version of the latest event recorded - denormalization
    version = Column(Integer, nullable=False)
