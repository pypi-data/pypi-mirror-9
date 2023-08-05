from __future__ import unicode_literals, print_function, absolute_import, \
    division
from contextlib import closing
from threading import Thread
from time import sleep
from urllib2 import urlopen, URLError

import os
from flask import request
from glask import Glask
import pytest
from selenium import webdriver
from werkzeug.serving import run_simple


class WrapMiddleware():
    def __init__(self):
        self.app = None
        self._default_app = Glask(__name__)
        self.port = 7000
        self.index_url = 'http://localhost:%d' % self.port

        # noinspection PyUnusedLocal
        @self._default_app.route('/')
        def index():
            return ''

        # noinspection PyUnusedLocal
        @self._default_app.route('/quit')
        def quit():
            request.environ['werkzeug.server.shutdown']()
            return ''

    def __call__(self, *args, **kwargs):
        return (self.app or self._default_app)(*args, **kwargs)


# noinspection PyUnusedLocal
@pytest.yield_fixture(scope='session')
def wsgi_server(request):
    server = WrapMiddleware()

    def target():
        run_simple(
            hostname='localhost', application=server, port=server.port,
            use_reloader=False,
        )

    thread = Thread(target=target)
    thread.start()
    # wait for server launched
    while True:
        try:
            with closing(urlopen(server.index_url + '/')) as f:
                f.read()
                break
        except URLError, e:
            if e.args[0].errno != 61:
                raise
        sleep(0.1)

    yield server

    with closing(urlopen(server.index_url + '/quit')) as f:
        f.read()
    thread.join()


# noinspection PyUnusedLocal
@pytest.yield_fixture
def live_app(request, wsgi_server, app):
    wsgi_server.app = app
    with app.test_request_context(wsgi_server.index_url):
        yield app
    wsgi_server.app = None


# noinspection PyUnusedLocal
@pytest.yield_fixture
def client(request, app):
    with app.test_request_context('http://localhost/'):
        yield app.test_client()


@pytest.yield_fixture
def browser():
    type = os.environ.get('TEST_BROWSER', 'firefox')
    b = {'firefox': webdriver.Firefox,
         'phantomjs': webdriver.PhantomJS}.get(type)()
    yield b
    b.quit()
