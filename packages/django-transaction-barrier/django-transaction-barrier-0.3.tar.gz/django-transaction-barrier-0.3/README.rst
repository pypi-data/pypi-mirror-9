django\_transaction\_barrier - transaction barriers for Django and Celery
=========================================================================

django\_transaction\_barrier provides a barrier-like abstraction for
transactions. A Django application developer can use a "transaction
barrier" to spawn a task within a transaction and guarantee that the
task blocks until it's able to access the updates made in the
transaction. django\_transaction\_barrier is designed with
`Celery <http://www.celeryproject.org/>`__ in mind and provides a Celery
task base class. Using the base class it's easy to write code that
atomically modifies the database and spawns a Celery task that executes
after the transaction commits.

Installation
------------

Install from source or use pip:

.. code:: sh

    pip install django_transaction_barrier

and add "django\_transaction\_barrier" to INSTALLED\_APPS in
settings.py:

.. code:: python

    INSTALLED_APPS = (
        'django_transaction_barrier',
        ...
    )

Usage
-----

.. code:: python

    from celery import task
    from django.db import transaction
    from django_transaction_barrier.celery import TransactionBarrierTask

    @task(base=TransactionBarrierTask)
    def do_something_task(model_id):
      value = Model.objects.get(id=model_id).value
      ...

    @transaction.atomic
    def kick_off_task(model, value):
        model.value = value
        do_something_task.apply_async_with_barrier(args=(model.id,))
        model.save()

Details
-------

If an application spawns an asynchronous TransactionBarrierTask the task
is guaranteed to execute eventually (assuming a durable task queue)
after the transaction commits. If the transaction aborts, the task
raises a TransactionAborted exception and does not execute. In
autocommit mode (i.e., "outside of a transaction")
TransactionBarrierTasks behave like normal Celery tasks.

If an application synchrnously executes a TransactionBarrierTask (e.g.,
with Celery eager mode) within a transaction, the task executes
immediately without waiting for the transaction to commit.

Implementation
--------------

django\_transaction\_barrier implements transaction barriers using row
insertion to signify a committed transaction and some DB-specifc logic
to detect an abort.

Related
-------

-  https://pypi.python.org/pypi/django-transaction-signals-do-not-use/1.0
-  https://django-transaction-hooks.readthedocs.org/en/latest/
-  https://code.djangoproject.com/ticket/14051
-  https://github.com/nickbruun/django\_atomic\_celery

django\_transaction\_barrier provides diffferent semantics than related
projects. It guarantees TransactionBarrierTask execution if the
transaction commits. Most related projects rely on monkey patching
Django's database backends to provide post commit hooks, which results
in a race: they (non-atomically) commit the transaction and then execute
the post commit hook, so they do not guarantee task execution.

As noted above, if an application synchrnously executes a
TransactionBarrierTask (e.g., with Celery eager mode) within a
transaction, the task executes immediately without waiting for the
transaction to commit.

Tests
-----

.. code:: sh

    docker build -t tests . && docker run tests

TODO
----

-  Add support for a mysql backend.

