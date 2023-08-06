from event_store.infrastructure.scripts.database_tools import create, delete, recreate

__author__ = 'Andriy Drozdyuk'
import argparse


def main():
    default_database_url = 'postgresql://postgres:test@localhost:5432/event_store'

    parser = argparse.ArgumentParser(description='Event Store Control Script')
    parser.add_argument('--database', choices=['create', 'delete', 'recreate'],
                        help='allows manipulation of the event store database.')
    parser.add_argument('--url', default=default_database_url, nargs='?',
                        help='database connection url')

    args = parser.parse_args()

    op = args.database
    url = args.url
    if op == 'create':
        create(url)
    elif op == 'delete':
        delete(url)
    elif op == 'recreate':
        recreate(url)
    else:
        print("Uknown operation!")




if __name__ == '__main__':
    main()
