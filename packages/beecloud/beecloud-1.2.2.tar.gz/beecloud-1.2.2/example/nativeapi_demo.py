import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import uuid
import os

from tornado.options import define, options
from bcpay.bc_api import BCApi

define("port", default=80, help="run on the given port", type=int)
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
BCApi.wx_app_id = 'wx419f04c4a731303d'
BCApi.wx_app_secret = '21e4b4593ddd200dd77c751f4b964963'
api = BCApi()
home = 'http://ask.beecloud.cn'
this_uri = '/wxmp/demo2/'
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            data = api.bc_prepare_nativeapi('tttt', str(uuid.uuid1()).replace('-',''), '1')
            self.render('templates/nativeapi_demo.html', data=data['code_url'])
            print data['code_url']
        except Exception, e:
            print e

def main():
    settings = {"static_path": os.path.join(os.path.dirname(__file__), "static")}
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/wxmp/demo2/", MainHandler),
    ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
