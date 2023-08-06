# -*- coding:utf-8 -*- 

import urllib2
import zlib
import gzip
from  StringIO import StringIO
import base64

if __name__ == '__main__':
    
    print base64.encodestring('abc')
    print base64.decodestring('XwU7ACHGoI5O5EetP2VKMskzi5InIBLoAGKej8hgA6NKGEP3APMK4Q')
    
#     filea = open(r'c:\b64.txt','r')   
#     lines = filea.readlines()
#     writefile=open(r'c:\d.txt','w')
#     for i in lines:   
#             word = i.strip()
#             b = base64.decodestring(word)
#             print b
#             writefile.write(b)
#             writefile.write('\n')
#     writefile.close()
#     filea.close()