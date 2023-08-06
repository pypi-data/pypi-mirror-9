from datetime import datetime
from .base import configure_app, create_app, flush_db_changes
from turbopress import model


class TurboPressAuthControllerTests(object):
    BLOG = ''

    @classmethod
    def blog_url(cls, url):
        if cls.BLOG:
            return url + '/' + cls.BLOG
        return url

    def setup(self):
        self.app = create_app(self.app_config, True)
        if self.BLOG:
            # Create another fake blog to make sure you don't get the wrong one.
            model.provider.create(model.Blog, {'name': 'ANOTHER BLOG'})
            model.provider.create(model.Blog, {'name': 'ANOTHER BLOG2'})
            model.provider.create(model.Blog, {'name': 'ANOTHER BLOG2'})
            model.provider.create(model.Blog, {'name': self.BLOG})
            flush_db_changes()

    def test_blog_new_authorized(self):
        resp = self.app.get(self.blog_url('/press/new'), status=302)
        assert 'http://localhost/press/edit' in resp.location

        resp = resp.follow(extra_environ={'REMOTE_USER': 'user'})
        assert 'action="/press/save"' in resp.text

    def test_blog_save(self):
        resp = self.app.get(self.blog_url('/press/new'), status=302)

        __, posts = model.provider.query(model.Article)
        post = posts[0]

        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
        resp = self.app.post('/press/save', {'uid': post.uid,
                                                  'title': '+Title',
                                                  'content': '+Content',
                                                  'description': '+Description',
                                                  'publish_date': now},
                                  status=302)

        __, posts = model.provider.query(model.Article)
        post = posts[0]
        assert post.title == '+Title'
        assert post.content == '+Content'
        assert post.description == '+Description'

        # Make sure that new posts are not published
        resp = self.app.get(self.blog_url('/press/index'))
        assert '''<div id="turbopress_articles">
</div>''' in resp.text, resp.text

    def test_blog_prevent_publish_empty(self):
        resp = self.app.get(self.blog_url('/press/new'), status=302)
        __, posts = model.provider.query(model.Article)
        post = posts[0]
        post_uid = post.uid

        resp = self.app.get('/press/publish', {'article': post_uid}, status=302)
        resp = resp.follow()

        assert 'Cannot publish an empty article' in resp.text

    def test_blog_publish(self):
        resp = self.app.get(self.blog_url('/press/new'), status=302)
        __, posts = model.provider.query(model.Article)
        post = posts[0]
        post_uid = post.uid

        post.content = '+Content'
        flush_db_changes()

        self.app.get('/press/publish', {'article': post_uid}, status=302)

        resp = self.app.get(self.blog_url('/press/index'))
        assert ('<a href="/press/view/%s">Untitled</a>' % post_uid) in resp.text, resp.text

    def test_blog_hide(self):
        resp = self.app.get(self.blog_url('/press/new'), status=302)
        __, posts = model.provider.query(model.Article)
        post = posts[0]
        post_uid = post.uid

        post.content = '+Content'
        flush_db_changes()

        self.app.get('/press/publish', {'article': post_uid}, status=302)
        self.app.get('/press/hide', {'article': post_uid}, status=302)

        # Make sure that new posts are not published
        resp = self.app.get(self.blog_url('/press/index'))
        assert '''<div id="turbopress_articles">
</div>''' in resp.text, resp.text


class TestTurboPressControllerAuthenticatedSQLA(TurboPressAuthControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('sqlalchemy')


class TestTurboPressControllerAuthenticatedMing(TurboPressAuthControllerTests):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app('ming')

