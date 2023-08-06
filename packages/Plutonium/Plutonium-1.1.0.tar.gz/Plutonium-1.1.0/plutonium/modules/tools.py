
import urllib2, urllib

def ucfirst(str):
    return str[0].upper() + str[1:]

def xml_element_to_storage(element):

    res = Storage()
    for item in element:
        res[item.tag] = item.text

    return res

class Storage(dict):

    def __getattr__(self, key):
        if key not in self:
            return None
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __hasattr__(self, key):
        return key in self


class FileReader(object):
    def read_all(self, file_name):
        with open(file_name) as f:
            content = f.read()
        return content


class SimpleResponse(Storage):
    def __init__(self, code, message = ''):
        self.code = code
        self.message = message

    def __str__(self):
        return "Code: %r, message: %s" % (self.code, self.message)

class HTTPResponse(object):
    def __init__(self, code, content, headers = {}):
        self.code = code
        self.content = content
        self.headers = headers

    def __str__(self):
        return "code: %d, headers: %s, content: %s" % (self.code, self.headers, self.content)

class URLLoader(object):
    def load(self, url, data = None, headers = {}):

        if data:
            data = urllib.urlencode(data)

        req = urllib2.Request(url, data, headers)

        try:
            response = urllib2.urlopen(req)
            return HTTPResponse(response.getcode(), response.read(), response.info().dict)
        except urllib2.URLError, e:
            raise
