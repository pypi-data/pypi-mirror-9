#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<roy@binux.me>
#         http://binux.me
# Created on 2014-12-10 20:36:27

import base64
from flask import Response
from flask.ext import login
from .app import app

login_manager = login.LoginManager()
login_manager.init_app(app)


class User(login.UserMixin):

    def __init__(self, id, password):
        self.id = id
        self.password = password

    def is_authenticated(self):
        if not app.config.get('webui_username'):
            return True
        if self.id == app.config.get('webui_username') \
                and self.password == app.config.get('webui_password'):
            return True
        return False

    def is_active(self):
        return self.is_authenticated()


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        return User(*api_key.split(":", 1))
    return None
app.login_response = Response(
    "need auth.", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
)


@app.before_request
def before_request():
    if app.config.get('need_auth', False):
        if not login.current_user.is_active():
            return app.login_response
