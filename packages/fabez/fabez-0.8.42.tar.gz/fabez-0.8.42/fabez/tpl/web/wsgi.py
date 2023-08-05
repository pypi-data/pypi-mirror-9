# -*- coding: utf-8 -*-

##################
# Note:
# This file was auto create by cabric, don't edit this file
# It will be always overwrite.
#########


import tornado.wsgi
import tornadoez
import tornadoez.web
from demo import settings
from demo.handlers import handlers


default_settings = tornadoez.web.build_settings(settings.pro, __file__)
tornadoez.settings = default_settings
application = tornado.web.Application(handlers, **default_settings)
app = tornado.wsgi.WSGIAdapter(application)

