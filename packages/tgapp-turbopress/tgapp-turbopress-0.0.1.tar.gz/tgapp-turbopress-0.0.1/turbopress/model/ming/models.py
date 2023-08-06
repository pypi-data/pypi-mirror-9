import os
from datetime import datetime
import shutil

import tg
from tg.caching import cached_property
from tg import request

from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty, MapperExtension
from ming.odm.declarative import MappedClass
from ming import schema as s, DESCENDING

from tgext.datahelpers.utils import slugify
from tgext.datahelpers.attachments import AttachedFile
from turbopress.model import DBSession
from tgext.pluggable import app_model

import mimetypes

mimetypes.init()

AttachmentType = tg.config.get('_turbopress', {}).get('attachment_type', AttachedFile)
ENABLE_ARTICLES_CACHE = tg.config.get('_turbopress', {}).get('enable_cache', False)
ARTICLE_CACHE_EXPIRE = tg.config.get('_turbopress', {}).get('cache_expire', 30 * 60)


class Blog(MappedClass):
    class __mongometa__:
        name = 'turbopress_blogs'
        session = DBSession
        indexes = [('name',)]

    _id = FieldProperty(s.ObjectId)
    name = FieldProperty(s.String, required=True, if_missing=u"Untitled")

    articles = RelationProperty('Article')

    @cached_property
    def uid(self):
        # Provided for seamless compatibility with SQLAlchemy
        return str(self._id)


class ArticleExt(MapperExtension):
    def before_update(self, instance, state, sess):
        instance.update_date = datetime.utcnow()


class Article(MappedClass):
    class __mongometa__:
        name = 'turbopress_articles'
        session = DBSession
        indexes = [('title',), ('published',), ('blog_id',), ('publish_date',)]
        extensions = [ArticleExt]

    _id = FieldProperty(s.ObjectId)
    title = FieldProperty(s.String, if_missing=u"Untitled")
    published = FieldProperty(s.Bool, if_missing=False)
    private = FieldProperty(s.Int, if_missing=0)
    tags = FieldProperty([s.String], if_missing=[])

    author_id = ForeignIdProperty(app_model.User)
    author = RelationProperty('User')

    blog_id = ForeignIdProperty(Blog)
    blog = RelationProperty('Blog')

    attachments = RelationProperty('Attachment')

    publish_date = FieldProperty(s.DateTime, if_missing=datetime.utcnow)
    update_date = FieldProperty(s.DateTime, if_missing=datetime.utcnow)

    description = FieldProperty(s.String, if_missing=u'Empty article, edit or delete this')
    content = FieldProperty(s.String, if_missing=u'')

    @cached_property
    def uid(self):
        # Provided for seamless compatibility with SQLAlchemy
        return str(self._id)

    @cached_property
    def slug(self):
        return slugify(self, self.title)

    @staticmethod
    def get_tagcloud(blog=None):
        if blog:
            try:
                blog = blog._id
            except:
                blog = Blog.query.find({'name': blog}).first()
                if not blog:
                    return []
                blog = blog._id

        pipeline = (
            {'$project': {'tags': 1}},
            {'$unwind': "$tags"},
            {'$group': {'_id': '', 'tags': {'$addToSet': '$tags'}}}
        )

        if blog:
            pipeline = ({'$match': {'blog_id': blog}},) + pipeline

        values = DBSession.impl.db.turbopress_articles.aggregate(pipeline)
        try:
            values = values['result'][0]['tags']
        except:
            values = []
        return values

    @staticmethod
    def get_published(blog=None):
        now = datetime.utcnow()
        filter = {'published': True,
                  'publish_date': {'$lte': now}}

        if blog:
            if not hasattr(blog, '_id'):
                blog = Blog.query.find({'name': blog}).first()

            try:
                filter.update({'blog_id': blog._id})
            except AttributeError:
                pass

        articles = Article.query.find(filter).sort([('publish_date', DESCENDING)])
        return articles

    @staticmethod
    def get_all(blog=None):
        filter = {}

        if blog:
            if not hasattr(blog, '_id'):
                blog = Blog.query.find({'name': blog}).first()

            try:
                filter.update({'blog_id': blog._id})
            except AttributeError:
                pass

        articles = Article.query.find(filter).sort([('publish_date', DESCENDING)])
        return articles.all()

    @property
    def blog_name(self):
        blog = self.blog
        if blog:
            return blog.name
        else:
            return ''

    def is_owner(self, identity):
        if not identity:
            return False

        return identity['user'] == self.author

    @property
    def caching_options(self):
        if not ENABLE_ARTICLES_CACHE:
            return dict()

        userid = request.identity['user'].user_id if request.identity else 'None'
        try:
            return dict(key='%s-%s-%s-%s' % (userid, 'turbopress-article',
                                             self._id, self.update_date.strftime('%Y-%m-%d-%H-%M-%S')),
                        expire=ARTICLE_CACHE_EXPIRE, type="memory")
        except (IndexError, ValueError):
            return dict()


class AttachmentExt(MapperExtension):
    def before_delete(self, instance, state, sess):
        try:
            shutil.rmtree(os.path.dirname(instance.content.local_path))
        except:
            pass


class Attachment(MappedClass):
    class __mongometa__:
        name = 'turbopress_attachments'
        session = DBSession
        indexes = [('article_id',)]
        extensions = [AttachmentExt]

    _id = FieldProperty(s.ObjectId)
    name = FieldProperty(s.String, required=True)

    article_id = ForeignIdProperty(Article)
    article = RelationProperty(Article)

    class AttachedFileProperty(FieldProperty):
        def __init__(self):
            super(self.__class__, self).__init__({'file': s.String(required=True),
                                                  'uuid': s.String(required=True),
                                                  'filename': s.String(required=True)})

        def __get__(self, instance, owner=None):
            if instance is None: return self
            v = super(self.__class__, self).__get__(instance)
            return AttachmentType(**v)

        def __set__(self, instance, value):
            value.write()

            value = {'uuid': value.uuid,
                     'file': value.local_path,
                     'filename': value.filename}
            return FieldProperty.__set__(self, instance, value)

    content = AttachedFileProperty()

    @cached_property
    def uid(self):
        # Provided for seamless compatibility with SQLAlchemy
        return str(self._id)

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.content.local_path, False)[0]

    @property
    def url(self):
        return self.content.url
