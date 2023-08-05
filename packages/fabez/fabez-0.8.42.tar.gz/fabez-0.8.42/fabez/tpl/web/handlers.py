# -*- coding: utf-8 -*-

import tornadoez
import tornadoez.web

class DemoHandler(tornadoez.web.RequestHandler):
    def get(self):
        self.write("Hello world")


handlers = [(r"/", DemoHandler)]


