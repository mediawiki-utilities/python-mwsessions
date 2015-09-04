Sessionization
==============

The primary purpose of this library is to provide facilities to aid in
`sessionizing` chronological sequences of activities into :class:`mwsessions.Session`.  You are provided with two options.  :func:`mwsessions.sessionize` takes an iterable of (user, timestamp, event_data)
triples and returns an iterator of :class:`mwsessions.Session`.  :class:`mwsessions.Sessionizer`, on the other hand, provides a :func:`~mwsessions.Sessionizer.process` method that allows you to process events one-at-a-time.

.. autofunction:: mwsessions.sessionize

.. autoclass:: mwsessions.Sessionizer

.. autoclass:: mwsessions.Session
