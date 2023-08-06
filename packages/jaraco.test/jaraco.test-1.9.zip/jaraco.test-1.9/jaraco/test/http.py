import copy

from mock import patch

class RequestsOverride(object):
    """
    Override 'requests' API to override specific requests and fall back to
    natural requests.
    """

    url_base = 'http://test'

    response_headers = {
        'Content-Type': 'application/json'
    }

    responses = dict()

    @classmethod
    def url(cls, *path_parts):
        """
        >>> RequestsOverride.url('foo', 'bar')
        'http://test/foo/bar'
        >>> RequestsOverride.url('foo', 'bar', '')
        'http://test/foo/bar/'

        Numbers are allowed:

        >>> RequestsOverride.url('foo', '3')
        'http://test/foo/3'
        """
        parts = [cls.url_base] + list(map(str, path_parts))
        return '/'.join(parts)

    def setup(self):
        self.patcher = patch('requests.session', create=True)
        self.mock = self.patcher.start()
        self.session = self.mock.return_value
        self.request = self.session.request
        self.response = self.request.return_value
        self.request.side_effect = self.do_request

    def do_request(self, *args, **kwargs):
        # use (method, url) as the key
        key = kwargs['method'], kwargs['url']

        if key not in self.responses:
            session = self.patcher.temp_original
            return session().request(*args, **kwargs)

        data = self.responses[key]

        # Data should have 'status', and may have 'content'
        self.response.status_code = data['status']
        if 'content' in data:
            self.response.content = data['content']
        if 'json' in data:
            self.response.json = lambda **params: data['json']

        self.response.headers = copy.copy(self.response_headers)
        self.response.headers.update(data.get('headers', {}))

        self.response.history = data.get('history', [])

        self.response.url = kwargs['url']
        if 'url' in data:
            self.response.url = data['url']
        return self.response

    def teardown(self):
        self.patcher.stop()
