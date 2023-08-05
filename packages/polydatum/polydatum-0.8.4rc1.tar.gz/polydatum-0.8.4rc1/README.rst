=========
Polydatum
=========

A Python encapsulated persistence layer for supporting many data access layers.

Very rough at the moment, only offers basic functionality.

Components
----------

### Context

The Context contains the current state for the active request. It should contain
all meta data associated with the request such as active user and HTTP request
parameters. It also provides access to Resources. When used in an HTTP framework
typically one context is created at the start of the HTTP request and it ends
before the HTTP response is sent.

When used with task managers such as Celery, the Context is created at the
start of a task and ends before the task result is returned.


### DAL

The DAL is the "Data Access Layer". The DAL is the registry for all Services.
To make call a method on a Service, you start with the DAL.

::

    result = dal.someservice.somemethod()


### Service

Services encapsulate business logic and data access. They are the Controller of
MVC-like applications. Services can be nested within other services.

::

    dal.register_services(
        someservice=SomeService().register_services(
            subservice=SubService()
        )
    )

    result = dal.someservice.subservice.somemethod()


### Resource

Resources are on-demand access to data backends such as SQL databases, key
stores, and blob stores. Resources have a setup and teardown phase. Resources
are only initialized and setup when they are first accessed within a context.
This lazy loading ensures that only the Resources that are needed for a
particular request are initialized.

The setup/teardown phases are particularly good for checking connections out
from a connection pool and checking them back in at the end of the request.

::

    def db_pool(context):
        conn = db.checkout_connection()
        yield conn
        db.checkin_connection(conn)

    class ItemService(Service):
        def get_item(self, id):
            return self._data_manager.db.query(
                'SELECT * FROM table WHERE id={id}',
                id=id
            )

    dm = DataManager()
    dm.register_services(items=ItemService())
    dm.register_resources(db=db_pool)

    with dm.dal() as dal:
        item = dal.items.get_item(1)


### Middleware

Middleware have a setup and teardown phase for each context. They are
particularly useful for managing transactions or error handling.

Context Middleware may only see and modify the Context. With the
Context, Context Middleware can gain access to Resources.

::

    def transaction_middleware(context):
        trans = new_transaction()
        trans.start()
        try:
            yield trans
        except:
            trans.abort()
        else:
            trans.commit()

    dm = DataManager()
    dm.register_context_middleware(transaction_middleware)


Principals
----------

- Methods that get an object should return `None` if an object can not be found.
- Methods that rely on an object existing to work (such as `create` that relies on a parent object) should raise `NotFound` if the parent object does not exist.
- All data access (SQL, MongoDB, Redis, S3, etc) must be done within a Service.

Considerations
--------------

### Middleware vs Resource

A Resource is created on demand. It's purpose is to create
a needed resource for a request and clean it up when done.
Middleware is ran on every context. It's purpose is to
do setup/teardown within the context.


Testing
-------

To run tests you'll need to install the test requirements:

    pip install -e .
    pip install -r src/tests/requirements.txt

Run tests:

    cd src/tests && py.test