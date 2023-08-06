# -*- coding: utf-8 -*-
"""The tgapp-turbopress package"""
import tg
from tg.configuration import milestones


def plugme(app_config, options):
    tg.config['_turbopress'] = options

    from turbopress import model
    milestones.config_ready.register(model.configure_models)
    milestones.environment_loaded.register(model.configure_provider)
    return dict(appid='press', global_helpers=False)

