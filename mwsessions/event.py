from collections import namedtuple

Event = namedtuple("Event", ['user', 'timestamp', 'i', 'data'])


def unpack_events(events):
    return list(e.data for e in events)
