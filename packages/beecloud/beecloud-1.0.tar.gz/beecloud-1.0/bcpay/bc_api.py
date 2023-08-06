# -*- coding: utf-8 -*-
import hashlib
import urllib
import json
from util import httpGet
class BCApi(object):
    bc_servers = ['123.57.71.81', '120.24.222.220', '115.28.40.236', '121.41.120.98', '58.211.191.85']
    #api version
    
    api_version = '1'
    #prepare sub url
    prepare_url = 'pay/wxmp/prepare'
    #basic configuration appid & appkey
    bc_app_id = ''
    bc_app_secret = ''
    #微信参数
    wx_app_id = '' #微信公众号唯一标识
    wx_app_secret = '' #微信公众号应用秘钥
    
    wx_fetch_openid_type = 'authorization_code'
    wx_sns_token_url_basic = 'https://api.weixin.qq.com/sns/oauth2/access_token?'
    wx_oauth_url_basic = 'https://open.weixin.qq.com/connect/oauth2/authorize?'
    wx_jsapi_type = 'JSAPI'
    wx_native_type = 'NATIVE'

    def __init__(self):
        if not self.bc_app_id or not self.bc_app_secret or not self.wx_app_id or not self.wx_app_secret:
            print 'beecloud或微信参数没有正确设置，请注意'
        self.server_index = 0
        return 

    def bc_sign(self):
        #return self.m.update(self.appid+self.appsecret)
        return hashlib.md5(self.bc_app_id + self.bc_app_secret).hexdigest()

    def bc_prepare_jsapi(self, openid, body, out_trade_no, total_fee):
        pp_data = {}
        pp_data['appId'] = self.bc_app_id
        pp_data['appSign'] = self.bc_sign()
        pp_data['openid'] = openid
        pp_data['trade_type'] = self.wx_jsapi_type
        pp_data['body'] = body
        pp_data['out_trade_no'] = out_trade_no
        pp_data['total_fee'] = total_fee
        params = json.dumps(pp_data)
        data = {}
        data['para'] = params
        hCode, value = httpGet('https://' + self.bc_servers[self.server_index] + '/' +
                self.api_version + '/' + self.prepare_url + '?'+ urllib.urlencode(data)) 
        if hCode :
            return json.loads(value)
        return None
        
    # 获取微信用户的openid，需要微信用户先登录，获得code
    # 获取code参考 fetch_code method
    def fetch_open_id(self, code):
        if not code :
            print 'need to login'
            return False, None
        url = self.create_fetch_open_id_url(code)
        hCode, hValue = httpGet(url)
        if hCode :
            return True, hValue
        else:
            return False, None

    # 获取openid的url生成方法
    def create_fetch_open_id_url(self, code):
        fetch_data = {}
        fetch_data['appid'] = self.wx_app_id
        fetch_data['secret'] = self.wx_app_secret
        fetch_data['grant_type'] = self.wx_fetch_openid_type
        fetch_data['code'] = code
        params = urllib.urlencode(fetch_data)
        return self.wx_sns_token_url_basic + params

    # 获取code 的url生成规则，redirect_url是微信用户登录后的回调页面，将会有code的返回
    def fetch_code(self, redirect_url):
        code_data = {}
        code_data['appid'] = self.wx_app_id
        code_data['redirect_uri'] = redirect_url
        code_data['response_type'] = 'code'
        code_data['scope'] = 'snsapi_base'
        code_data['state'] = 'STATE#wechat_redirect' 
        params = urllib.urlencode(code_data)
        return self.wx_oauth_url_basic + params
