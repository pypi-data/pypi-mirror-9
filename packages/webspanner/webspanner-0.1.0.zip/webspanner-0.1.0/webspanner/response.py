import time
import asyncio
from http.cookies import SimpleCookie
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler
from .utils import MultiDict

STATUS_MAP = BaseHTTPRequestHandler.responses


def status_line(status):
    line = STATUS_MAP[status][0]
    return "{} {}".format(status, line).encode('ascii')


class HttpResponse:
    def __init__(self, writer, app, status=200, version=1.1, content_type='text/html'):
        self.status = int(status)
        self.cookies = SimpleCookie()
        self.writer = writer
        self._app = app
        self.headers = MultiDict([
            ('Content-Encoding', 'UTF-8'),
            ('Content-Type', content_type),
        ])
        self.version = version
        # self.content_type = content_type
        self.headers_sent = False
        self.closed = False

    def send_headers(self):
        if self.headers_sent:
            return
        # send status line first
        self.writer.write("HTTP/{} {} {}\r\n"
            .format(self.version, self.status, STATUS_MAP[self.status][0]).encode())

        # headers = self._get_headers_list(headers)
        # for k,v in self.headers:
        for key in self.headers:
            values = self.headers.getall(key)
            # Write all the values of the key
            [ self.writer.write("{}:{}\r\n".format(key, v).encode()) for v in values ]
        self.writer.write("\r\n".encode())
        self.headers_sent = True


    def write(self, chunk):
        """Writes chunk of data to a stream by using different writers.
        writer uses filter to modify chunk of data.
        write_eof() indicates end of stream.
        writer can't be used after write_eof() method being called.
        write() return drain future.
        """
        if self.headers_sent == False:
            self.send_headers()
        if isinstance(chunk, str):
            chunk = chunk.encode()
        self.writer.write(chunk)

    def writelines(self, data_lists):
        if self.headers_sent == False:
            self.send_headers()
        self.writer.writelines(data_lists)

    def write_eof(self):
        # do some check
        self.writer.write_eof()

    def close(self):
        self.writer.close()
        self.closed = True

    def render_template(self, name, *args, **kwargs):
        """
        Usage:

        req.render_template("index.tpl",{
            "name": "Chen",
        })
        """
        pass

    @asyncio.coroutine
    def abort(self, req, code=404):
        self.status = code
        handler = self._app.get_errors_handler(code)
        if not handler:
            self.status = 404
            self.write("404 Error handler Not Found\r\n")
            self.close()
            return
        yield from handler(req, self)
        self.close()

    def _get_headers_list(self, headers=None):
        if headers == None:
            headers = self.headers
        if isinstance(headers, bytes):
            h = headers
        elif isinstance(headers, str):
            h = headers.encode()
        elif isinstance(headeers, list):
            h = [(x.encode('ascii'), y.encode('ascii')) for x, y in headers]
        for c in self.cookies.values():
            h.append((b'Set-Cookie', c.output(header='').encode('ascii')))
        return h


    def set_cookie(self, name, value='', max_age=None, path='/',
                   domain=None, secure=False, httponly=False):
        self.cookies[name] = value
        if max_age is not None:
            self.cookies[name]['max-age'] = max_age
            if not max_age:
                expires_date = 'Thu, 01-Jan-1970 00:00:00 GMT'
            else:
                dt = formatdate(time.time() + max_age)
                expires_date = '%s-%s-%s GMT' % (dt[:7], dt[8:11], dt[12:25])

            self.cookies[name]['expires'] = expires_date


        if path is not None:
            self.cookies[name]['path'] = path
        if domain is not None:
            self.cookies[name]['domain'] = domain
        if secure:
            self.cookies[name]['secure'] = True
        if httponly:
            self.cookies[name]['httponly'] = True

    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, max_age=0, path=path, domain=domain)
