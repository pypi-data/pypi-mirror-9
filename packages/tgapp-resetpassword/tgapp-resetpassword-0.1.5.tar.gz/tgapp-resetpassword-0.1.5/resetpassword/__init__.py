# -*- coding: utf-8 -*-
"""The tgapp-resetpassword package"""

import tg
from tg.configuration import milestones


def plugme(app_config, options):
    app_config['_pluggable_resetpassword_config'] = options

    from resetpassword import model
    milestones.config_ready.register(model.configure_models)
    milestones.environment_loaded.register(model.configure_provider)
    return dict(appid='resetpassword', global_helpers=False)