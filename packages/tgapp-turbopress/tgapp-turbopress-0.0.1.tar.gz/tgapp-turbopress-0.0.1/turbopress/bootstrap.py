# -*- coding: utf-8 -*-
"""Setup the Turbopress application"""

from turbopress import model
from tgext.pluggable import app_model


def bootstrap(command, conf, vars):
    print 'Bootstrapping Turbopress...'

    p = model.provider.create(app_model.Permission, dict(permission_name='turbopress',
                                                         description='Can manage blogs and posts'))

    __, g = model.provider.query(app_model.Group, filters=dict(group_name='managers'), limit=1)
    if g:
        g = g[0]
        g.permissions = g.permissions + [p]
        model.DBSession.flush()
