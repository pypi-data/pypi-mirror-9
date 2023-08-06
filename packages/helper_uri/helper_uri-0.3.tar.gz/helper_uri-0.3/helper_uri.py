import urllib

class HelperString(object):
    @staticmethod
    def to_uni(obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                return obj.decode('gbk')
        elif isinstance(obj, (int, long)):
            return unicode(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        else:
            return obj

    @staticmethod
    def to_str(obj):
        if isinstance(obj, unicode):
            return obj.encode('utf-8')
        else:
            return obj


class HelperURI(object):
    @staticmethod
    def urljoin(end_with_slash, *args):
        """
        >>> HelperURI.urljoin(False, *('http://127.0.0.1:8000', 'dumb_upload'))
        'http://127.0.0.1:8000/dumb_upload'

        >>> HelperURI.urljoin(True, *('http://127.0.0.1:8000', 'dumb_upload'))
        'http://127.0.0.1:8000/dumb_upload/'
        """
        last = args[0]
        for i in args[1:]:
            last = '%s/%s' % (last.strip('/'), i.strip('/'))

        if end_with_slash:
            if last[-1] != '/':
                last += '/'
        return last

    @staticmethod
    def path2full_uri(path, prefix=None, default_protocol='http', end_with_slash=True):
        """
        >>> HelperURI.path2full_uri(path='127.0.0.1:8000', end_with_slash=False)
        'http://127.0.0.1:8000'

        >>> HelperURI.path2full_uri(path='/api', prefix='192.168.1.100', end_with_slash=False)
        'http://192.168.1.100/api'

        >>> HelperURI.path2full_uri(path='/api/v1', prefix='192.168.1.100', default_protocol='https', end_with_slash=True)
        'https://192.168.1.100/api/v1/'
        """
        if path.startswith('http'):
            return path

        if prefix:
            if not prefix.startswith('http'):
                prefix = '%s://%s' % (default_protocol, prefix)

            parts = [prefix, path]
            return HelperURI.urljoin(end_with_slash, *parts)
        else:
            if end_with_slash:
                uri = '%s://%s' % (default_protocol, path)
                return uri.strip('/') + '/'
            else:
                uri = '%s://%s' % (default_protocol, path)
                return uri.strip('/')


    @staticmethod
    def dict2query_string(pair):
        d = {}
        for k, v in pair.iteritems():
            d[k] = HelperString.to_str(v)
        return urllib.urlencode(d)