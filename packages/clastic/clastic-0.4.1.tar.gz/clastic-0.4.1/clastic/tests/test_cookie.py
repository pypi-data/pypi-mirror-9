# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from nose.tools import eq_

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from clastic import Application, render_basic
from clastic.middleware.cookie import SignedCookieMiddleware

from common import cookie_hello_world


def test_cookie_mw():
    cookie_mw = SignedCookieMiddleware()
    _ = repr(cookie_mw)  # coverage, lol
    app = Application([('/', cookie_hello_world, render_basic),
                       ('/<name>/', cookie_hello_world, render_basic)],
                      middlewares=[cookie_mw])
    ic = Client(app, BaseResponse)
    resp = ic.get('/')
    yield eq_, resp.status_code, 200
    yield eq_, resp.data, 'Hello, world!'
    resp = ic.get('/Kurt/')
    yield eq_, resp.data, 'Hello, Kurt!'
    resp = ic.get('/')
    yield eq_, resp.data, 'Hello, Kurt!'

    ic2 = Client(app, BaseResponse)
    resp = ic2.get('/')
    yield eq_, resp.data, 'Hello, world!'


def test_cookie_expire():
    cookie_mw = SignedCookieMiddleware(data_expiry=0)
    app = Application([('/', cookie_hello_world, render_basic),
                       ('/<name>/', cookie_hello_world, render_basic)],
                      middlewares=[cookie_mw])
    ic = Client(app, BaseResponse)
    resp = ic.get('/')
    yield eq_, resp.status_code, 200
    yield eq_, resp.data, 'Hello, world!'
    resp = ic.get('/Kurt/')
    yield eq_, resp.data, 'Hello, Kurt!'
    resp = ic.get('/')
    yield eq_, resp.data, 'Hello, world!'

    ic2 = Client(app, BaseResponse)
    resp = ic2.get('/')
    yield eq_, resp.data, 'Hello, world!'
