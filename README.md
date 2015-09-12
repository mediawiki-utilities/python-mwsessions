# MediaWiki Sessions

This library provides a set of utilities for group MediaWiki user actions into
sessions.  

* **Installation:** ``pip install mwsessions``
* **Documentation:** https://pythonhosted.org/mwsessions
* **Repositiory:** https://github.com/mediawiki-utilities/python-mwsessions
* **License:** MIT

## Basic example

    >>> import mwsessions
    >>>
    >>> user_events = [
    ...     ("Willy on wheels", 20150101000000, {'rev_id': 1}),
    ...     ("Walter", 20150101000001, {'rev_id': 2}),
    ...     ("Willy on wheels", 20150101000001, {'rev_id': 3}),
    ...     ("Walter", 20150101000002, {'rev_id': 4}),
    ...     ("Willy on wheels", 20150101001001, {'rev_id': 5})
    ... ]
    >>>
    >>> for user, events in mwsessions.sessionize(user_events):
    ...     (user, events)
    ...
    ('Willy on wheels', [{'rev_id': 1}, {'rev_id': 3}])
    ('Walter', [{'rev_id': 2}, {'rev_id': 4}])
    ('Willy on wheels', [{'rev_id': 5}])

## Author
* Aaron Halfaker -- https://github.com/halfak
