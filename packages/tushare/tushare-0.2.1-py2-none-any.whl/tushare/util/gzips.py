# -*- coding:utf-8 -*- 

import urllib2
from gzip import GzipFile
from StringIO import StringIO
import zlib


class ContentEncodingProcessor(urllib2.BaseHandler):
    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip, deflate")
        return req
    
    def http_response(self, req, resp):
        old_resp = resp
        print resp.headers.get("content-encoding")
        # gzip
        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile(
                        fileobj=StringIO(resp.read()),
                        mode="r"
                      )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            print zlib.decompress(gz.read())
            resp.msg = old_resp.msg
        # deflate
        if resp.headers.get("content-encoding") == "deflate":
            gz = StringIO( deflate(resp.read()) )
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
            resp.msg = old_resp.msg
        return resp

# deflate support
import zlib
def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
    try:               # so on top of all there's this workaround:
        return zlib.decompress(data, -zlib.MAX_WBITS)
    except zlib.error:
        return zlib.decompress(data)
    
    
if __name__ == '__main__':
    encoding_support = ContentEncodingProcessor
    opener = urllib2.build_opener( encoding_support, urllib2.HTTPHandler )
 
    #直接用opener打开网页，如果服务器支持gzip/defalte则自动解压缩
    content = opener.open('http://finance.sina.com.cn/realstock/company/sz000601/hisdata/klc_cm.js?day=2015-03-12').read()
#     print content
    
    
    s = 'ROmvHT0llP5IT5SDc9rZSHKLAJguIhcKN6tj9h5Z7hCisUd40Z9jRBx7+qb6Cr+OkGniBLtgbzQwIi+p98oumxSa3zISjplqcpdAZS7JhO68kai93/HG+9NzJFjy0Gcpe3mhWS2pjU4NJ0ZcReFiGz6fCuKLgF7nL45pxi4TdJ1pApQml0gBOL6yapvBX7Io5HsxNLH7T0RluUv+EOlTeMkLKN+GziWXUOXw9IQI/oGlvm5B'
    print deflate(StringIO(s))