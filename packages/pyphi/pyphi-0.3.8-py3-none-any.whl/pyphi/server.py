#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Server
~~~~~~

Handles JSON-RPC calls to the remote API.
"""

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager

from .remote_api import dispatcher


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    try:
        response = Response(response.json, mimetype='application/json')
        # Add CORS headers.
        # TODO*** Restrict this before launch.
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    # XXX fix error handling
    finally:
        return response


def listen():
    run_simple('localhost', 4000, application)
