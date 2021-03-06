from . import defaults
from .sessionizer import Sessionizer


def sessionize(user_events, cutoff=defaults.CUTOFF):
    """
    Clusters user sessions from a sequence of user events.  Note that,
    `event` data will simply be returned in the case of a revert.

    This function serves as a convenience wrapper around calls to
    :class:`~mw.lib.sessions.Cache`'s :meth:`~mw.lib.sessions.Cache.process`
    method.

    :Parameters:
        user_events : iter( (user, timestamp, event) )
            an iterable over tuples of user, timestamp and event data.

            * user : `hashable`
            * timestamp : :class:`mw.Timestamp`
            * event : `mixed`

        cutoff : int
            the maximum time between events within a user session

    :Returns:
        a iterator over :class:`~mw.lib.sessions.Session`

    :Example:
        >>> import mwsessions
        >>>
        >>> user_events = [
        ...     ("Willy on wheels", 20150101000000, {'rev_id': 1}),
        ...     ("Walter", 20150101000001, {'rev_id': 2}),
        ...     ("Willy on wheels", 20150101000001, {'rev_id': 3}),
        ...     ("Walter", 100035, {'rev_id': 4}),
        ...     ("Willy on wheels", 103602, {'rev_id': 5})
        ... ]
        >>>
        >>> for user, events in mwsessions.sessionize(user_events):
        ...     (user, events)
        ...
        ('Willy on wheels', [{'rev_id': 1}, {'rev_id': 3}])
        ('Walter', [{'rev_id': 2}, {'rev_id': 4}])
        ('Willy on wheels', [{'rev_id': 5}])


    """

    # Construct the session manager
    sessionizer = Sessionizer(cutoff)

    # Apply the events
    for user, timestamp, event in user_events:

        for session in sessionizer.process(user, timestamp, event):
            yield session

    # Yield the left-overs
    for session in sessionizer.get_active_sessions():
        yield session
