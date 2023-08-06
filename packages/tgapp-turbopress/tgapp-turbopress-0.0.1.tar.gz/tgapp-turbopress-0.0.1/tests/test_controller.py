from datetime import datetime
from .base import configure_app, create_app, flush_db_changes
from turbopress import model


class TurboPressControllerTests(object):
    def setup(self):
        self.app = create_app(self.app_config, False)

    def test_index(self):
        resp = self.app.get('/')
        assert 'HELLO' in resp.text

    def test_blog_index(self):
        a = model.provider.create(model.Article, {'title': 'Hello',
                                                  'content': 'World',
                                                  'published': True})
        article_id = a.uid
        flush_db_changes()

        resp = self.app.get('/press')
        assert 'turbopress_articles' in resp.text
        assert ('<a href="/press/view/%s">Hello</a>' % article_id) in resp.text, resp.text

    def test_blog_new_unauth(self):
        self.app.get('/press/new', status=401)


class TestTurboPressControllerSQLA(TurboPressControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('sqlalchemy')


class TestTurboPressControllerMing(TurboPressControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('ming')

