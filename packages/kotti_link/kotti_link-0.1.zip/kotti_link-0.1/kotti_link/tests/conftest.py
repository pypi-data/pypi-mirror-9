from pytest import fixture

pytest_plugins = "kotti"


@fixture
def extra_principals(db_session):
    from kotti.security import get_principals
    P = get_principals()
    P[u'bob'] = dict(name=u'bob', title=u"Bob")
    P[u'frank'] = dict(name=u'frank', title=u"Frank")
    P[u'group:bobsgroup'] = dict(name=u'group:bobsgroup', title=u"Bob's Group")
    P[u'group:franksgroup'] = dict(name=u'group:franksgroup',
        title=u"Frank's Group")


@fixture(scope='session')
def custom_settings():
    import kotti_link.resources
    kotti_link.resources  # make pyflakes happy
    return {
        'kotti.configurators': 'kotti_link.kotti_configure'
        }
