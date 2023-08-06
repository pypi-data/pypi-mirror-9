import os
from datetime import datetime

import tg
from tg import request, config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from sqlalchemy import Table, ForeignKey, Column, Index
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation
from sqlalchemy import event, func, select

from tgext.datahelpers.utils import slugify
from tgext.datahelpers.fields import Attachment as DatahelpersAttachment, AttachedFile
from turbopress.model import DBSession
from tgext.pluggable import app_model, primary_key

import mimetypes
mimetypes.init()

DeclarativeBase = declarative_base()

AttachmentType = tg.config.get('_turbopress', {}).get('attachment_type', AttachedFile)
ENABLE_ARTICLES_CACHE = tg.config.get('_turbopress', {}).get('enable_cache', False)
ARTICLE_CACHE_EXPIRE = tg.config.get('_turbopress', {}).get('cache_expire', 30*60)


class Blog(DeclarativeBase):
    __tablename__ = 'turbopress_blogs'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(100), nullable=False, default=u"Untitled", index=True)


class Article(DeclarativeBase):
    __tablename__ = 'turbopress_articles'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(Unicode(150), nullable=False, default=u"Untitled", index=True)
    published = Column(Integer, nullable=False, default=0, index=True)
    private = Column(Integer, nullable=False, default=0)

    author_id = Column(Integer, ForeignKey(primary_key(app_model.User)))
    author = relation(app_model.User, backref=backref('articles'))

    blog_id = Column(Integer, ForeignKey(primary_key(Blog)), nullable=True, index=True)
    blog = relation(Blog, backref=backref('articles'), lazy='joined')

    publish_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    update_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Unicode(1024), nullable=False,
                         default=u'Empty article, edit or delete this')
    content = Column(Unicode(64000), nullable=False, default=u'')

    @hybrid_property
    def tags(self):
        return [x[0] for x in DBSession.query(Tagging.name).filter(Tagging.article_id == self.uid)]

    @property
    def slug(self):
        return slugify(self, self.title)

    @tags.setter
    def tags(self, value):
        self.tagging = [Tagging(blog_id=self.blog_id, article_id=self.uid, name=t) for t in value]

    @tags.comparator
    def tags(cls):
        class TaggingComparator(Comparator):
            def __eq__(self, other):
                return self.expression.any(Tagging.name == other)
        return TaggingComparator(cls.tagging)

    @staticmethod
    def get_tagcloud(blog=None):
        tags = DBSession.query(Tagging.name)

        if blog:
            try:
                blog = blog.uid
            except:
                blog = DBSession.query(Blog).filter_by(name=blog).first()
                if not blog:
                    return []

                blog = blog.uid

            tags = tags.filter_by(blog_id=blog)

        return tags.group_by(Tagging.name).all()

    @staticmethod
    def get_published(blog=None):
        now = datetime.utcnow()
        articles = DBSession.query(Article).filter_by(published=True)\
                                           .filter(Article.publish_date<=now)

        if blog:
            try:
                blog = blog.name
            except:
                pass
            articles = articles.join(Blog).filter(Blog.name==blog)

        articles = articles.order_by(Article.publish_date.desc())
        return articles

    @staticmethod
    def get_all(blog=None):
        articles = DBSession.query(Article)
        if blog:
            try:
                blog = blog.name
            except:
                pass
            articles = articles.join(Blog).filter(Blog.name==blog)
        articles = articles.order_by(Article.publish_date.desc())
        return articles

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
                                             self.uid,
                                             self.update_date.strftime('%Y-%m-%d-%H-%M-%S')),
                                             expire=ARTICLE_CACHE_EXPIRE, type="memory")
        except (IndexError, ValueError):
            return dict()


class Attachment(DeclarativeBase):
    __tablename__ = 'turbopress_attachments'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(16), nullable=False)
    content = Column(DatahelpersAttachment(AttachmentType))

    article_id = Column(Integer, ForeignKey(Article.uid))
    article = relation(Article, backref=backref('attachments', cascade='all, delete-orphan'))

    @staticmethod
    def delete_file(mapper, connection, obj):
        try:
            os.unlink(obj.content.local_path)
        except:
            pass

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.content.local_path, False)[0]

    @property
    def url(self):
        return self.content.url

event.listen(Attachment, 'before_delete', Attachment.delete_file)


class Tagging(DeclarativeBase):
    __tablename__ = 'turbopress_tagging'

    blog_id = Column(Integer, ForeignKey(Blog.uid), index=True)
    article_id = Column(Integer, ForeignKey(Article.uid), nullable=False, primary_key=True)
    name = Column(Unicode(64), nullable=False, primary_key=True)

    article = relation(Article, backref=backref('tagging', cascade='all, delete-orphan'))

    @staticmethod
    def on_change(mapper, connection, obj):
        obj.name = obj.name.strip().lower()

event.listen(Tagging, 'before_insert', Tagging.on_change)
event.listen(Tagging, 'before_update', Tagging.on_change)
