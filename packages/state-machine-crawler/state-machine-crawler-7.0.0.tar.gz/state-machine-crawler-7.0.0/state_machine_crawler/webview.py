import os
import mimetypes
import urllib
from functools import partial
import threading
import urllib2
import socket
from wsgiref.simple_server import make_server, WSGIRequestHandler

from werkzeug.wrappers import Response, Request
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import wrap_file

from .svg_serializer import Serializer


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SilentHandler(WSGIRequestHandler):

    def log_message(self, *args, **kwargs):
        pass


class WebView(object):
    """

    state_machine(:class:`StateMachineCrawler <state_machine_crawler.StateMachineCrawler>` instance)
        State machine to be monitored

    Sample usage:

    >>> app = WebView(state_machine)
    >>> try:
    >>>     app.start()
    >>>     state_machine.verify_all_states()
    >>> except TransitionError, e:
    >>>     print e
    >>> except KeyboardInterrupt:
    >>>     pass
    >>> app.stop()

    Once the code is executed, a web service monitoring your state machine shall be started under
    http://localhost:8666. The url shall be printed to stdout to ease the access.

    An html page of the web service is a dynamic view of the state graph that represents the state machine.
    """

    HOST = 'localhost'

    def __init__(self, state_machine):
        self._serializer = Serializer(state_machine)
        self._viewer_thread = threading.Thread(target=self._run_server)
        self._alive = False
        self._server = None

        url_map = [
            Rule("/", endpoint=partial(self._static, path="index.html")),
            Rule("/kill", endpoint=None),
            Rule("/graph.svg", endpoint=self._graph),
            Rule("/<string:path>", endpoint=self._static)
        ]

        self._url_map = Map(url_map)

    def _graph(self, request):
        resp = Response(repr(self._serializer))
        resp.mimetype = self._serializer.mimetype
        return resp

    def _static(self, request, path):
        local_path = os.path.join(PROJECT_DIR, "webview")
        file_name = path.lstrip("/").replace("/", os.path.sep)

        if os.path.exists(local_path):
            root = local_path
        else:
            root = "/usr/share/state_machine_crawler"

        abs_path = os.path.join(root, file_name)
        resp = Response()

        if not (os.path.exists(abs_path) and os.path.isfile(abs_path)):
            resp.status_code = 404
            return resp

        fil = open(abs_path)
        resp.direct_passthrough = True
        resp.response = wrap_file(request.environ, fil)

        url = urllib.pathname2url(abs_path)
        resp.mimetype = mimetypes.guess_type(url)[0]

        return resp

    def __call__(self, environ, start_response):
        urls = self._url_map.bind_to_environ(environ)
        endpoint, params = urls.match()
        if endpoint is None:
            resp = Response("Killed")
        else:
            resp = endpoint(Request(environ), **params)
        return resp(environ, start_response)

    def _run_server(self):
        self._server = httpd = make_server(self.HOST, 8666, self, handler_class=SilentHandler)
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Started the server at http://%s:%d" % (self.HOST, httpd.server_port))
        while self._alive:
            httpd.handle_request()

    def start(self):
        if self._alive:
            return
        self._alive = True
        self._viewer_thread.start()

    def stop(self):
        if not self._alive:
            return
        self._alive = False
        try:
            urllib2.urlopen("http://%s:%d/kill" % (self.HOST, self._server.server_port), timeout=3)
        except socket.error:
            pass
        self._viewer_thread.join()
