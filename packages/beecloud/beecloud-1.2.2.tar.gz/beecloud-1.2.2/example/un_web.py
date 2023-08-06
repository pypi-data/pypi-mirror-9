import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import uuid

from tornado.options import define, options
from bcpay.bc_api import BCApi

define("port", default=8088, help="run on the given port", type=int)
BCApi.bc_app_id = 'c5d1cba1-5e3f-4ba0-941d-9b0a371fe719'
BCApi.bc_app_secret = '39a7a518-9ac8-4a9e-87bc-7885f33cf18c'
api = BCApi()
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        data = api.bc_un_web_pay(str(uuid.uuid1()).replace('-',''), 'sample_trace_id', '1', 'sample order desc', 'http://beecloud.cn')
        print data
        self.write(data['html']) 
def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/unweb/demo/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
