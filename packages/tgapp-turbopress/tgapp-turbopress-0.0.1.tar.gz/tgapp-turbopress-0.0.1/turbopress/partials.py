from tg import expose, request
from turbopress import model
from tgext.pluggable import plug_url, app_model
from turbopress.lib.forms import SearchForm

WEEK_EXPIRE = 3600*24*7


@expose('genshi:turbopress.templates.articles')
def articles(articles=None, blog=None):
    if articles is None:
        articles = model.Article.get_published(blog)
    return dict(articles=articles)


@expose('genshi:turbopress.templates.article_preview')
def article_preview(article):
    user = 'anonymous'
    if request.identity:
        try:
            user = request.identity['user']._id
        except AttributeError:
            from tgext.pluggable import primary_key
            user = getattr(request.identity['user'], primary_key(app_model.User).key)

    return dict(article=article, tg_cache=dict(key='%s-%s-%s' % (article.uid, user,
                                                                 article.update_date.strftime('%Y-%m-%d_%H:%M:%S')),
                                               expire=WEEK_EXPIRE,
                                               type='memory'))


@expose('genshi:turbopress.templates.tagcloud')
def tagcloud(blog, tags):
    return dict(blog=blog, tags=tags)


@expose('genshi:turbopress.templates.search')
def search(blog, value=''):
    return dict(form=SearchForm, value=dict(blog=blog, text=value),
                action=plug_url('turbopress', '/search'))


@expose('genshi:turbopress.templates.articles_excerpts')
def excerpts(articles=None, blog=None):
    if articles is None:
        articles = model.Article.get_published(blog)
    return dict(articles=articles)


@expose('genshi:turbopress.templates.excerpt')
def excerpt(article):
    return article_preview(article)
