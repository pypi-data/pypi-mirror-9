#!/usr/bin/env python
# coding=utf-8

try:
    import urllib2
    import urllib
except ImportError:
    from urllib import request as urllib2
    from urllib import parse as urllib

class cole_requests:
    def __init__(self):
        pass

    @classmethod
    def get(self, url, to=10, *args, **kwargs):
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req, timeout=to)
        return res_data.read()

    @classmethod
    def post(self, url, data={}, to=10, *args, **kwargs):
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data=data.encode('utf-8'))
        res_data = urllib2.urlopen(req, timeout=to)
        return res_data.read()


if __name__ == '__main__':
    print('Usage:')
    print('\t cole_requests.get(url,...)')
    print('\t cole_requests.post(url, data, ...)')
    print('\t a = cole_requests()')
    print('\t a.get(url,...)')
    print('\t a.post(url, data, ...)')
