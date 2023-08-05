# -*- coding: utf-8 -*-

##################
# Note:
# This file was auto create by cabric, don't edit this file
# It will be always overwrite.
#########


from cliez.loader import ArgLoader
import tornadoez.web
import tornado.ioloop

from settings import settings
from handlers import handlers


if __name__ == "__main__":
    from datetime import datetime
    a = ArgLoader((
        ('Useage app.py port'),
        '',
        '',
        'Options:',
        ('--debug', 'debug flag'),
        ('--help', 'print help document', '-h'),
    ))

    try:
        port = int(a.argv[1])
    except:
        port = 9001

    debug = a.options.get('--debug') or False

    print("[tornado]:server start, bind port {}, begin at: {}.".format(port, datetime.now()))

    if debug:
        from settings import settings_debug
        print("[tornado]:debug mode enabled.")
        settings['debug'] = True
        settings['css_debug'] = True
        settings['js_debug'] = True
        settings.update(settings_debug)
        pass

    default_settings = tornadoez.web.build_settings(settings)

    application = tornado.web.Application(handlers, **default_settings)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
