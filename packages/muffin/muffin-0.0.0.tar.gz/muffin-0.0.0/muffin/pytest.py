# Configure your tests here
import asyncio

import pytest
import webtest
from aiohttp.protocol import HttpVersion11, HttpVersion10, RawRequestMessage
from aiohttp.multidict import CIMultiDict
from aiohttp.web import (
    AbstractMatchInfo,
    HTTPException,
    Request,
    RequestHandler,
    RequestHandlerFactory,
    StreamResponse,
)


class TestRequestHandler(RequestHandler):

    @asyncio.coroutine
    def handle_request(self, message, payload):
        app = self._app
        request = Request(app, message, payload, self.transport, self.reader, self.writer)
        try:
            match_info = yield from self._router.resolve(request)

            assert isinstance(match_info, AbstractMatchInfo), match_info

            request._match_info = match_info
            handler = match_info.handler

            for factory in reversed(self._middlewares):
                handler = yield from factory(app, handler)
            resp = yield from handler(request)

            if not isinstance(resp, StreamResponse):
                raise RuntimeError(
                    ("Handler {!r} should return response instance, "
                     "got {!r} [middlewares {!r}]").format(
                         match_info.handler,
                         type(resp),
                         self._middlewares))
        except HTTPException as exc:
            resp = exc

        return resp


class TestRequest(webtest.TestRequest):

    """ Support asyncio loop. """

    def call_application(self, application, catch_exc_info=False):
        if self.is_body_seekable:
            self.body_file_raw.seek(0)

        http_version = HttpVersion10 if self.http_version == 'HTTP/1.0' else HttpVersion11
        message = RawRequestMessage(
            self.method, self.path, http_version, CIMultiDict(self.headers), False, False)
        payload = self.body_file_raw

        loop = asyncio.get_event_loop()
        handler = RequestHandlerFactory(
            application, application.router, handler=TestRequestHandler, loop=loop)()
        response = loop.run_until_complete(handler.handle_request(message, payload))

        return response.status, response.headers.items(), [response.body], None


class TestApp(webtest.TestApp):

    RequestClass = TestRequest


@pytest.fixture(scope='session')
def app():
    """ Provide an example application. """
    from app import app
    return app


@pytest.fixture(scope='session')
def loop(request):
    """ Create and provide asyncio loop. """
    loop = asyncio.new_event_loop()
    request.addfinalizer(lambda: loop.close())
    return loop


@pytest.fixture(scope='function')
def client(app, loop):
    client = TestApp(app, lint=False)
    client.exception = webtest.AppError
    return client
