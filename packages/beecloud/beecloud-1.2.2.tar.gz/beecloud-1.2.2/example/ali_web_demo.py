# -*- coding: utf-8 -*-
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
        try:
            data = api.bc_ali_web_pay('白开水', '0.01', str(uuid.uuid1()).replace('-',''), 'localhost/aliwebpay/demo_return')
            print data
            sHtml = data['sbHtml']
            #支付宝网页支付的html
            self.write(sHtml)
            biz_data = {"goods_info": { 
                    "id": "10001",
                    "name": "water ha",
                    "price": "0.01",
                    "desc": "nice "
                    },
                "ext_info": {
                    "single_limit": "2",
                    "user_limit": "3",
                    "logo_name": "BeeCloud"
                    },
                "need_address":"F",
                "trade_type":"1",
                "notify_url":"http://beecloud.cn/ali_test/aliqrcode/notify_url.php"
                } 
            data = api.bc_ali_qr_pay('add', biz_data, None)
            #支付宝扫码支付的二维码图片地址
            #self.write('<img src="'+data['qr_img_url'] + '"/>')
        except Exception, e:
            print e

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/aliwebpay/demo/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
