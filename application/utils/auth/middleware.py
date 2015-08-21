import uuid
from http.cookies import SimpleCookie


class AuthMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def session_start_response(status, headers, exc_info=None):
            sid = environ['session.id']
            if not sid:
                sid = str(uuid.uuid1()).replace('-', '')
                headers.append(('Set-cookie', 'sid=%s' % sid))
            return start_response(status, headers, exc_info)

        cookies = self.get_cookies(environ)
        sid = cookies.get('sid', None)
        sid = sid.value if sid else None
        environ['session.id'] = sid
        return self.app(environ, session_start_response)

    @staticmethod
    def get_cookies(environ):
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])
        return cookie