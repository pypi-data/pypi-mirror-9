import urllib
def httpGet(url):
    try:
        f = urllib.urlopen(url)
        s = f.read()
        return True, s
    except:
        return False, None
