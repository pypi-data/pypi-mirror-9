# coding=utf-8

from __future__ import print_function
from socket import AF_INET, SOL_SOCKET, SO_REUSEADDR

from gevent import wait as gwait
from gevent.socket import socket
from gevent.pywsgi import WSGIServer
from gevent.os import fork
from gevent.threadpool import ThreadPool
from gevent.event import Event

from ..config import settings
from ..signaler import Signaler
from ..interface import BaseEngine
from ..util import app_path


class Engine(BaseEngine, Signaler):

    #
    # 引擎本身只需实现 BaseEngine 接口，信号处理属于额外增强功能。
    # 子进程创建、退出都属于系统信号范畴，统一由 Singaler 处理。
    #

    def __init__(self, server):
        self._server = server
        self._pool = ThreadPool(settings.CPUS * 4)
        self._listen_sock = None
        self._wsgi_server = None

        BaseEngine.__init__(self, server)
        Signaler.__init__(self)

    def run(self):
        if settings.NEED_PATCH_SOCKET_SSL:
            # gevent.pywsgi启动
            from gevent.monkey import patch_socket, patch_ssl
            patch_socket()
            # 在patch socket之后，如果使用https会出错，需要连ssl也patch掉
            patch_ssl()

        if not settings.NEED_GEVENT_THREADPOOL:
            def sync(func, *args, **kwargs):
                return func(*args, **kwargs)
            self.async_execute = sync

        self._listen_sock = socket(family=AF_INET)
        self._listen_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._listen_sock.bind((settings.HOST, settings.PORT))
        self._listen_sock.listen(2048)
        self._listen_sock.setblocking(0)

        if settings.WORKERS == 1:
            # 只有一个worker 启用单进程运行
            self.serve_forever()
        else:
            self.fork_workers(settings.WORKERS or settings.CPUS + 1)
            self.parent_execute()

    def fork_workers(self, num):
        for i in range(num):
            if fork() == 0:
                self.worker_execute()
                exit(0)

    def worker_execute(self):
        Signaler.worker_execute(self)

        self.serve_forever()

        # 等待所有处理结束，超时 10 秒。
        hasattr(self._wsgi_server, "__graceful__") and gwait(timeout=10)

    def serve_forever(self):
        # 启动服务器。
        kwargs = settings.HTTPS and \
            {k: app_path("ssl/" + v) for k, v in (("keyfile", settings.HTTPS_KEY), ("certfile", settings.HTTPS_CERT))} or \
            {}

        if settings.SUPPORT_WEBSOCKET:
            from geventwebsocket.handler import WebSocketHandler
            kwargs["handler_class"] = WebSocketHandler

        self._wsgi_server = WSGIServer(self._listen_sock, self._server.execute, log=None, **kwargs)
        self._wsgi_server.serve_forever()

    def worker_stop(self, graceful):
        stop = lambda *args: self._wsgi_server and self._wsgi_server.stop()
        graceful and (setattr(self._wsgi_server, "__graceful__", True), stop()) or stop()

    def async_execute(self, func, *args, **kwargs):
        e = Event()
        g = self._pool.apply_async(func, args, kwargs, callback=lambda ret: e.set())
        e.wait()
        return g.get()
