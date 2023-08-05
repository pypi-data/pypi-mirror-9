

def test_link(db_session, root):
    """ Basic link constructor and add to root """
    from kotti_link.resources import Link

    content = Link(link='')
    # assert content.type_info.addable(content, DummyRequest()) is True
    root['content'] = content


def test_link_attributes(db_session, root):
    """ The link attribute should be set """
    from kotti_link.resources import Link
    root['content'] = Link(link=u'http://google.com')
    assert root['content'].link == u'http://google.com'


def test_link_copy(db_session, root):
    """ Link objects should be copied """
    from kotti_link.resources import Link
    root['content'] = Link(link=u'http://google.com')
    root['copy-of'] = root['content'].copy(title=u'another link')
    assert root['copy-of'].title == u'another link'
