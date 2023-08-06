# -*- coding: utf-8 -*-
import logging
import tg
from tgext.pluggable import PluggableSession

log = logging.getLogger('tgapp-turbopress')

DBSession = PluggableSession()
provider = None

Article = None
Attachment = None
Blog = None


def init_model(app_session):
    DBSession.configure(app_session)


def configure_models():
    global provider, Article, Attachment, Blog, Tagging

    if tg.config.get('use_sqlalchemy', False):
        log.info('Configuring Turbopress for SQLAlchemy')
        from turbopress.model.sqla.models import Article, Attachment, Blog, Tagging
        from sprox.sa.provider import SAORMProvider
        provider = SAORMProvider(session=DBSession, engine=False)
    elif tg.config.get('use_ming', False):
        log.info('Configuring Turbopress for Ming')
        from turbopress.model.ming.models import Article, Attachment, Blog
        from sprox.mg.provider import MingProvider
        provider = MingProvider(DBSession)
    else:
        raise ValueError('Turbopress should be used with sqlalchemy or ming')


def configure_provider():
    if tg.config.get('use_sqlalchemy', False):
        provider.engine = DBSession.bind
