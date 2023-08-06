from event_store.infrastructure.persistence.schema.event_store_schema import Base
from sqlalchemy import create_engine


def create(url):
    engine = create_engine(url)
    Base.metadata.create_all(engine, checkfirst=True)


def delete(url):
    print("Dropping database.")
    engine = create_engine(url)
    Base.metadata.drop_all(engine, checkfirst=True)


def recreate(url):
    engine = create_engine(url)
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine, checkfirst=True)

