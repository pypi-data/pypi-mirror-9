Event Store
===========

Event Store is an implementation of the `Events as a Storage Mechanism <https://cqrs.wordpress.com/documents/events-as-storage-mechanism/>`__ concept (`PDF here <https://dl.dropboxusercontent.com/u/9162958/CQRS/Events%20as%20a%20Storage%20Mechanism%20CQRS.pdf>`__). It is an implementation of the actual storage for events. The implementation follows the excellent article by Greg Young: `Building an Event Storage <https://cqrs.wordpress.com/documents/building-event-storage/>`__. (`PDF Here <https://dl.dropboxusercontent.com/u/9162958/CQRS/Building%20an%20Event%20Storage%20CQRS.pdf>`__). Reading the linked articles should provide sufficient understanding of the code.

Installation
============

1. To create tables, run `infrastructure/scripts/main.py` with an option `--database create`. This naively assumes that your sql engine is postgresql, and is located at `postgresql://postgres:test@localhost:5432`, and you have created a database named `event_store`. (You can change this in `main.py`).
2. For usage example see `tests/test_event_store.py`.
   
Functionality
=============

Currently a Sql backend is provided with simple Pickle serialization.

Why It Exists
=============
There didn't seem to be any python native event storage implementations.

Contributing
============

The implementation is minimalistic, but pull requests are welcome. Please file an issue with an approriate pull request.
