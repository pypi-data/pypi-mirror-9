from mock import patch
from pyramid.httpexceptions import HTTPFound

from kotti.resources import get_root
from kotti.security import get_principals
from kotti.testing import testing_db_url

from kotti_link.resources import Link
from kotti_link.views import LinkView


class TestViews:

    def setup(self):
        from kotti import main

        settings = {'sqlalchemy.url': testing_db_url(),
                    'kotti.secret': 'dude'}
        with patch('kotti.resources.initialize_sql'):
            main({}, **settings)

    def test_view_view(self, db_session, dummy_request):
        root = get_root()
        link = root['link'] = Link(link=u'/', title=u'Test Link')
        view = LinkView(link, dummy_request)
        assert(isinstance(view.view(), dict))

    def test_redirect_view(self, db_session, dummy_request, extra_principals):
        self.setup()
        root = get_root()
        link = root['link'] = Link(link=u'/', title=u'Test Link')
        view = LinkView(link, dummy_request)
        result = view.redirect()
        assert(isinstance(result, HTTPFound))
        assert result.status == u'302 Found'

        bob = get_principals()[u'bob']
        dummy_request.user = bob
        acl = [('Allow', 'system.Everyone', 'edit')]
        link.__acl__ = acl
        view = LinkView(link, dummy_request)
        assert(isinstance(view.redirect(), dict))

    def test_redirect_internal(self, db_session, dummy_request):
        from kotti.resources import Document

        self.setup()

        root = get_root()
        root['test-doc'] = Document(title='Test Doc')
        link = root['link'] = Link(link=u'/test-doc', title=u'Test Link')
        view = LinkView(link, dummy_request)
        result = view.redirect()
        assert result.location == '/test-doc'

    def test_redirect_external(self, db_session, dummy_request):
        from kotti.resources import Document

        self.setup()
        root = get_root()
        root['test-doc'] = Document(title='Test Doc')
        link = root['link'] = Link(link=u'http://some-wild-example.org',
                                   title=u'Test Link')
        view = LinkView(link, dummy_request)
        result = view.redirect()
        assert result.location == 'http://some-wild-example.org'

    def test_popup_view(self, db_session, dummy_request):
        from kotti.resources import Document

        self.setup()
        root = get_root()
        root['test-doc'] = Document(title='Test Doc')
        link = root['link'] = Link(link=u'/test-doc',
                                   title=u'Test Link')
        view = LinkView(link, dummy_request)
        result = view.popup()
        assert(isinstance(result, dict))
