# -*- coding: utf-8 -*-
"""Main Controller"""
import tg
from tg import TGController
from tg import expose, flash, require, url, request, redirect, validate, config, abort
from tg.decorators import cached_property, paginate
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates

from turbopress import model
from turbopress.helpers import *
from turbopress.lib.forms import UploadForm, get_article_form, DataGrid, \
    inject_datagrid_resources, SpinnerIcon
from tgext.datahelpers.attachments import AttachedFile
from tgext.pluggable import plug_url, plug_redirect
from webhelpers.html.builder import HTML
from datetime import datetime
from tgext.ajaxforms.ajaxform import formexpose
from tgext.crud import EasyCrudRestController
from turbopress.lib.dal import ModelEntityConverter, make_paginable

AttachmentType = config.get('_turbopress',{}).get('attachment_type', AttachedFile)

upload_form = UploadForm()
articles_table = DataGrid(fields=[(l_('Actions'), lambda row:link_buttons(row, 'edit', 'delete', 'hide', 'publish')),
                                  (l_('Blog'), lambda row:row.blog and row.blog.name),
                                  (l_('Title'), lambda row:HTML.a(row.title,
                                                                  href=plug_url('turbopress', '/view/%s'%row.uid,
                                                                                lazy=True))),
                                  (l_('Tags'), comma_separated_tags),
                                  (l_('Author'), 'author'),
                                  (l_('Publishing'), lambda row:format_published(row) + ', ' + format_date(row))])

attachments_table = DataGrid(fields=[(l_('Actions'), lambda row:link_buttons(row, 'rmattachment')),
                                     (l_('Name'), 'name'),
                                     (l_('Preview'), attachment_preview),
                                     (l_('Url'), lambda row:format_link(row.url))])


class BlogsController(EasyCrudRestController):
    allow_only = predicates.has_permission('turbopress')
    title = "Manage Blogs"

    __form_options__ = {
        '__omit_fields__': ['articles', 'uid', '_id']
    }

    __table_options__ = {
        '__omit_fields__': ['uid', '_id', 'articles']
    }


class RootController(TGController):
    @cached_property
    def blogs(self):
        class ModelBoundBlogsController(BlogsController):
            model = model.Blog

        return ModelBoundBlogsController(model.DBSession.wrapped_session)

    @expose('genshi:turbopress.templates.index')
    @paginate('articles')
    def index(self, blog='', *args, **kw):
        articles = make_paginable(model.Article.get_published(blog))
        tags = model.Article.get_tagcloud(blog)
        return dict(articles=articles, tags=tags, blog=blog, search='')

    _default = index

    @expose('genshi:turbopress.templates.article')
    @validate(dict(article=ModelEntityConverter('Article', slugified=True)), error_handler=index)
    def view(self, article, **kw):
        visible = False

        if article.published and article.publish_date <= datetime.utcnow():
            visible = True
        elif request.identity and article.author == request.identity['user']:
            visible = True
        elif request.identity and 'turbopress' in request.identity['groups']:
            visible = True

        if not visible:
            return plug_redirect('turbopress', '/')

        tg.hooks.notify('turbopress.before_view_article', args=(article, kw))

        return dict(article=article,
                    tg_cache=article.caching_options)

    @require(predicates.has_permission('turbopress'))
    @expose('genshi:turbopress.templates.manage')
    @paginate('articles')
    def manage(self, blog='', *args, **kw):
        articles = model.Article.get_all(blog)
        return dict(table=articles_table, articles=articles,
                    create_action=plug_url('turbopress', '/new/'+blog))

    @require(predicates.has_permission('turbopress'))
    @expose('genshi:turbopress.templates.edit')
    def new(self, blog=None, **kw):
        inject_datagrid_resources(attachments_table)

        if 'uid' not in kw:
            if blog:
                __, blog = model.provider.query(model.Blog, filters=dict(name=blog))
                if blog:
                    blog = blog[0]

            article_data = {'author': request.identity['user'],
                            'blog': blog and blog}

            tg.hooks.notify('turbopress.before_create_article', args=(article_data, kw))
            article = model.provider.create(model.Article, article_data)
            tg.hooks.notify('turbopress.after_create_article', args=(article, kw))
        else:
            article = model.provider.get_obj(model.Article, params=dict(uid=kw['uid'],
                                                                        _id=kw['uid']))

        return plug_redirect('turbopress', '/edit/%s' % article.uid)

    @require(predicates.has_permission('turbopress'))
    @expose('genshi:turbopress.templates.edit')
    def edit(self, uid=None, *args, **kw):
        if not uid:
            abort(404)

        article = model.provider.get_obj(model.Article, params=dict(uid=uid,
                                                                    _id=uid))
        if not article:
            abort(404)

        inject_datagrid_resources(attachments_table)

        value = {
            'uid': article.uid,
            'title': article.title,
            'description': article.description,
            'tags': comma_separated_tags(article),
            'publish_date': article.publish_date.strftime('%Y-%m-%dT%H:%M'),
            'content': article.content
        }

        tg.hooks.notify('turbopress.before_edit_article', args=(article, value))

        return dict(article=article, value=value, blog=article.blog and article.blog.name or '',
                    form=get_article_form(), action=plug_url('turbopress', '/save'),
                    upload_form=upload_form, upload_action=plug_url('turbopress', '/attach'))

    @require(predicates.has_permission('turbopress'))
    @validate(get_article_form(), error_handler=edit)
    @expose()
    def save(self, *args, **kw):
        article = model.provider.get_obj(model.Article, params=dict(uid=kw['uid'],
                                                                    _id=kw['uid']))

        tg.hooks.notify('turbopress.before_save_article', args=(article, kw))

        article.title = kw['title']
        article.description = kw['description']
        article.content = kw['content']
        article.publish_date = kw['publish_date']
        article.update_date = datetime.utcnow()
        article.tags = tuple(set(x.strip().lower() for x in kw['tags'].split(',')))

        flash(_('Articles successfully saved'))
        return plug_redirect('turbopress', '/manage/'+article.blog_name)

    @require(predicates.has_permission('turbopress'))
    @formexpose(upload_form, 'turbopress.templates.attachments')
    def upload_form_show(self, **kw):
        article = model.provider.get_obj(model.Article, params=dict(uid=kw['article'],
                                                                    _id=kw['article']))

        return dict(value=kw, table=attachments_table, attachments=article.attachments)

    @require(predicates.has_permission('turbopress'))
    @validate(upload_form, error_handler=upload_form_show)
    @expose('genshi:turbopress.templates.attachments')
    def attach(self, **kw):
        article = model.provider.get_obj(model.Article, params=dict(uid=kw['article'],
                                                                    _id=kw['article']))

        attachment_data = dict(name=kw['name'],
                               article=article,
                               content=AttachmentType(kw['file'].file,
                                                      kw['file'].filename))

        tg.hooks.notify('turbopress.on_attachment_upload', args=(article, attachment_data))

        model.provider.create(model.Attachment, attachment_data)

        return dict(value=dict(article=article.uid),
                    ajaxform=upload_form,
                    ajaxform_id='attachments_form',
                    ajaxform_action=upload_form.action,
                    ajaxform_spinner=SpinnerIcon(),
                    table=attachments_table,
                    attachments=article.attachments)

    @require(predicates.has_permission('turbopress'))
    @validate(dict(attachment=ModelEntityConverter('Attachment')))
    @expose()
    def rmattachment(self, attachment):
        article = attachment.article

        tg.hooks.notify('turbopress.on_attachment_remove', args=(article, attachment))

        model.provider.delete(model.Attachment, params=dict(uid=attachment.uid,
                                                            _id=attachment.uid))

        flash(_('Attachment successfully removed'))
        return plug_redirect('turbopress', '/edit/%s'%article.uid)

    @require(predicates.has_permission('turbopress'))
    @validate(dict(article=ModelEntityConverter('Article')), error_handler=manage)
    @expose()
    def publish(self, article):
        if not article.content:
            flash(_('Cannot publish an empty article'))
        else:
            article.published=True
            flash(_('Article published'))

        tg.hooks.notify('turbopress.on_article_publishing', args=(article, True))
        return plug_redirect('turbopress', '/manage/'+article.blog_name)

    @require(predicates.has_permission('turbopress'))
    @validate(dict(article=ModelEntityConverter('Article')), error_handler=manage)
    @expose()
    def hide(self, article):
        article.published=False
        flash(_('Article hidden'))

        tg.hooks.notify('turbopress.on_article_publishing', args=(article, False))
        return plug_redirect('turbopress', '/manage/'+article.blog_name)

    @require(predicates.has_permission('turbopress'))
    @validate(dict(article=ModelEntityConverter('Article')), error_handler=manage)
    @expose()
    def delete(self, article):
        tg.hooks.notify('turbopress.on_article_delete', args=(article))

        model.provider.delete(model.Article, params=dict(uid=article.uid,
                                                         _id=article.uid))

        flash(_('Article successfully removed'))
        return plug_redirect('turbopress', '/manage/'+article.blog_name)

    @expose('genshi:turbopress.templates.index')
    @paginate('articles')
    def search(self, blog='', text=None, tags=None):
        filters = dict()
        extra_args = {}
        if text:
            filters['content'] = text
            extra_args['substring_filters'] = ['content']

        if blog:
            __, blogs = model.provider.query(model.Blog, filters=dict(name=blog))
            blog_entry = blogs[0]

            # While sprox SA provider does cast values, the Ming one
            # doesn't. So we must ensure that we actually use an ObjectId
            # and not a string, or it won't find anything.
            filters['blog_id'] = getattr(blog_entry, '_id', blog_entry.uid)

        if tags:
            filters['tags'] = tags

        if 'tags' not in filters and 'content' not in filters:
            flash(_('No search rule has been specified'))
            return plug_redirect('turbopress', '/'+blog)

        count, articles = model.provider.query(model.Article,
                                               filters=filters,
                                               **extra_args)

        blog_tags = model.Article.get_tagcloud(blog)
        return dict(articles=articles, tags=blog_tags, blog=blog, search=text)
