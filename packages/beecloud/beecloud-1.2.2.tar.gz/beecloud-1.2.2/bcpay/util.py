import urllib2
import ssl
def httpGet(url):
    try:
        gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        f = urllib2.urlopen(url, context = gcontext)
        s = f.read()
        return True, s
    except :
        try:
            f = urllib2.urlopen(url)
            s = f.read()
            return True, s
        except:
            return False, None
