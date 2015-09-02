from nose.tools import eq_

from ..sessionizer import Sessionizer


def test_sessionizer():
    sessionizer = Sessionizer(cutoff=2)

    user_sessions = list(sessionizer.process("foo", 1))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process("bar", 2))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process("foo", 2))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process("bar", 10))
    eq_(len(user_sessions), 2)

    user_sessions = list(sessionizer.get_active_sessions())
    eq_(len(user_sessions), 1)

def test_none_comparison():
    sessionizer = Sessionizer(cutoff=2)

    user_sessions = list(sessionizer.process((None, "123"), 0, "AIDS"))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process((1, "foobar"), 1, "Foobar"))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process((1, "foobar"), 1, None))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process((None, "234"), 1, "Foobar"))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process((None, "234"), 1, "Barfoo"))
    eq_(user_sessions, [])

    user_sessions = list(sessionizer.process((1, "foobar"), 10))
    eq_(len(user_sessions), 3)
