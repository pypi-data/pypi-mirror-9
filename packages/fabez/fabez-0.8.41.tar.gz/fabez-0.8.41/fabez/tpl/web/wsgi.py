# -*- coding: utf-8 -*-

##################
# Note:
# This file was auto create by cabric, don't edit this file
# It will be always overwrite.
#########


import tornado.wsgi
import tornadoez.web
from settings import settings
from handlers import handlers


default_settings = tornadoez.web.build_settings(settings)
application = tornado.web.Application(handlers, **default_settings)
app = tornado.wsgi.WSGIAdapter(application)

