'''
Defines a Group class for running and managing servers, as well as a set of
base server types.

The following information is needed to start a server:
1- handler / wsgi app
2- address
3- ssl preference

'''
import os
import socket
import threading
import traceback
import collections

if hasattr(os, "fork"):
    import ufork
    import fcntl
    import errno
else:
    ufork = None
import gevent
from gevent import pywsgi
import gevent.server
import gevent.socket
import gevent.pool

import clastic
from faststat import nanotime

from support import async
from support import context
from support.crypto import SSLContext

import ll
ml = ll.LLogger()
ml2 = context.get_context().log.get_module_logger()

# TODO: autoadd console and meta servers

DEFAULT_NUM_WORKERS = 1
DEFAULT_MAX_CLIENTS = 1024  # per worker
DEFAULT_SOCKET_LISTEN_SIZE = 128


class Group(object):
    def __init__(self, wsgi_apps=(), stream_handlers=(), custom_servers=(),
                 prefork=None, daemonize=None, **kw):
        """\
        Create a new Group of servers which can be started/stopped/forked
        as a group.

        *wsgi_apps* should be of the form  [ (wsgi_app, address, ssl), ...  ]

        *stream_handlers* should be of the form  [ (handler_func, address), ...  ]

        *custom_servers* should be of the form [ (server_class, address), ... ]
        where server_class refers to subclasses of gevent.server.StreamServer
        which define their own handle function

        address here refers to a tuple (ip, port), or more generally anything which is
        acceptable as the address parameter to
        `socket.bind() <http://docs.python.org/2/library/socket.html#socket.socket.bind>`_.

        `handler_func` should have the following signature: f(socket, address), following
        the `convention of gevent <http://www.gevent.org/servers.html>`_.
        """
        ctx = context.get_context()
        self.wsgi_apps = list(wsgi_apps or [])
        self.stream_handlers = list(stream_handlers or [])
        self.custom_servers = list(custom_servers or [])

        self.prefork = prefork
        self.daemonize = daemonize
        # max number of concurrent clients per worker
        self.max_clients = kw.pop('max_clients', DEFAULT_MAX_CLIENTS)
        self.num_workers = kw.pop('num_workers', DEFAULT_NUM_WORKERS)
        self.post_fork = kw.pop('post_fork', None)  # post-fork callback
        self.server_log = kw.pop('gevent_log', None)

        self.meta_address = kw.pop('meta_address', None)
        self.console_address = kw.pop('console_address', None)
        self._require_client_auth = kw.pop('require_client_auth', True)

        if kw:
            raise TypeError('unexpected keyword args: %r' % kw.keys())

        self.client_pool = gevent.pool.Pool(ctx.max_concurrent_clients)
        self.servers = []
        self.socks = {}

        # we do NOT want a gevent socket if we're going to use a
        # thread to manage our accepts; it's critical that the
        # accept() call *blocks*
        socket_type = gevent.socket.socket if not ufork else socket.socket

        for app, address, ssl in wsgi_apps:
            sock = _make_server_sock(address, socket_type=socket_type)

            if isinstance(ssl, SSLContext):
                ssl_context = ssl
            elif ssl:
                ssl_context = ctx.ssl_context
            else:
                ssl_context = None
            if ssl_context:
                if self._no_client_auth_req:
                    server = MultiProtocolWSGIServer(
                        sock, app, spawn=self.client_pool, context=ssl_context)
                else:
                    server = SslContextWSGIServer(
                        sock, app, spawn=self.client_pool, context=ssl_context)
            else:
                server = ThreadQueueWSGIServer(sock, app)
            server.log = self.server_log or RotatingGeventLog()
            self.servers.append(server)
            self.socks[server] = sock
            # prevent a "blocking" call to DNS on each request
            # (NOTE: although the OS won't block, gevent will dispatch
            # to a threadpool which is expensive)
            server.set_environ({'SERVER_NAME': socket.getfqdn(address[0]),
                                'wsgi.multiprocess': True})
        for handler, address in self.stream_handlers:
            sock = _make_server_sock(address)
            server = gevent.server.StreamServer(sock, handler, spawn=self.client_pool)
            self.servers.append(server)
        for server_class, address in self.custom_servers:
            # our stated requirement is that users provide a subclass
            # of StreamServer, which would *not* know about our thread
            # queue.  consequently we can't give it a blocking socket
            sock = _make_server_sock(address)
            server = server_class(sock, spawn=self.client_pool)
            self.servers.append(server)
        if self.console_address is not None:
            try:
                sock = _make_server_sock(self.console_address)
            except Exception as e:
                print "WARNING: unable to start backdoor server on port", ctx.backdoor_port, repr(e)
            else:
                server = gevent.server.StreamServer(sock, console_sock_handle, spawn=self.client_pool)
                self.servers.append(server)
        # set all servers max_accept to 1 since we are in a pre-forked/multiprocess environment
        for server in self.servers:
            server.max_accept = 1

    def iter_addresses(self):
        # TODO: also yield app/handler?
        for wsgi_app, address, ssl_ctx in self.wsgi_apps:
            yield address
        for handler, address in self.stream_handlers:
            yield address
        for server, address in self.custom_servers:
            yield address

    def serve_forever(self):
        ctx = context.get_context()
        ctx.running = True
        try:
            # set up greenlet switch monitoring
            import greenlet
            greenlet.settrace(ctx._trace)
        except AttributeError:
            pass  # oh well
        if not self.prefork:
            self.start()
            log_msg = 'Group initialized and serving forever...'
            ctx.log.critical('GROUP.INIT').success(log_msg)
            if ctx.dev and ctx.dev_service_repl_enabled and os.isatty(0):
                async.start_repl({'server': ctx.server_group})
            try:
                while 1:
                    async.sleep(1.0)
            finally:
                self.stop()
            return
        if not ufork:
            raise RuntimeError('attempted to run pre-forked on platform without fork')
        if ctx.tracing:  # a little bit hacky, disable tracing in aribter
            self.trace_in_child = True
            ctx.set_greenlet_trace(False)
        else:
            self.trace_in_child = False
        self.arbiter = ufork.Arbiter(
            post_fork=self._post_fork, child_pre_exit=self.stop, parent_pre_stop=ctx.stop,
            size=self.num_workers, sleep=async.sleep, fork=gevent.fork, child_memlimit=ctx.worker_memlimit)
        if self.daemonize:
            pgrpfile = os.path.join(ctx.process_group_file_path,
                                   '{0}.pgrp'.format(ctx.appname))
            self.arbiter.spawn_daemon(pgrpfile=pgrpfile)
        else:
            self.arbiter.run()

    def _post_fork(self):
        # TODO: revisit this with newer gevent release
        hub = gevent.hub.get_hub()
        hub.loop.reinit()  # reinitializes libev
        hub._threadpool = None  # eliminate gevent's internal threadpools
        gevent.sleep(0)  # let greenlets run
        # finally, eliminate our threadpools
        ctx = context.get_context()
        ctx.thread_locals = threading.local()
        # do not print logs failures -- they are in stats
        ctx.log_failure_print = False
        if self.daemonize:
            ll.use_std_out()
        if ctx.sampling:
            ctx.set_sampling(False)
            ctx.set_sampling(True)

        if self.post_fork:
            self.post_fork()
        msg = 'successfully started process {pid}'
        ctx.log.critical('WORKER', 'START').success(msg, pid=os.getpid())
        if self.trace_in_child:  # re-enable tracing LONG SPIN detection
            ctx.set_greenlet_trace(True)  # if it was enabled before forking
        self.start()

    def start(self):  # TODO
        errs = {}
        for server in self.servers:
            try:
                server.start()
            except Exception as e:
                traceback.print_exc()
                errs[server] = e
        if errs:
            raise RuntimeError(errs)

    def stop(self, timeout=30.0):  # TODO: .shutdown()?
        gevent.joinall([gevent.spawn(server.stop, timeout)
                        for server in self.servers], raise_error=True)


def _make_server_sock(address, socket_type=gevent.socket.socket):
    ml.ld("about to bind to {0!r}", address)
    ml2.info('listen_prep').success('about to bind to {addr}', addr=address)
    sock = socket_type()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)

    # NOTE: this is a "hint" to the OS than a strict rule about backlog size
    with context.get_context().log.critical('LISTEN') as _log:
        sock.listen(DEFAULT_SOCKET_LISTEN_SIZE)
        if ufork is not None:
            # we may fork, so protect ourselves
            flags = fcntl.fcntl(sock.fileno(), fcntl.F_GETFD)
            fcntl.fcntl(sock.fileno(), fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
        #ml.la("Listen to {0!r} gave this socket {1!r}", address, sock)
        _log.success('Listen to {addr} gave {sock}', addr=address, sock=sock)
    return sock


class MakeFileCloseWSGIHandler(pywsgi.WSGIHandler):
    '''
    quick work-around to re-enable gevent's work-around of the
    makefile() call in the pywsgi handler keeping sockets alive
    past their shelf life
    '''
    def __init__(self, socket, address, server, rfile=None):
        if rfile is None and hasattr(socket, "_makefile_refs"):
            rfile = socket.makefile()
            # restore gEvent's work-around of not letting wsgi.environ['input']
            # keep the socket alive in CLOSE_WAIT state after client is gone
            # to work with async.SSLSocket
            socket._makefile_refs -= 1
        self.state = context.get_context().markov_stats['wsgi_handler'].make_transitor('new')
        super(MakeFileCloseWSGIHandler, self).__init__(socket, address, server, rfile)

    def handle_one_request(self):
        self.state.transition('handling_request')
        ret = super(MakeFileCloseWSGIHandler, self).handle_one_request()
        if not ret:
            self.state.transition('done')
        return ret

    def run_application(self):
        self.state.transition('running_application')
        return super(MakeFileCloseWSGIHandler, self).run_application()

    def process_result(self):
        self.state.transition('writing_response')
        ret = super(MakeFileCloseWSGIHandler, self).process_result()
        self.state.transition('done')
        return ret


# Threaded accept queue implementation
#
# poll(2) and its relatives require that all processes monitoring a
# file descriptor be informed when it becomes readable or writable.
# Consequently, sharing a socket across multiple processes that call
# accept(2) after poll(2) says that socket is readable results in an
# inefficient distribution of connections; *all* processes are woken
# up when a new connection comes in, and which one actually *gets* the
# connection is hard to predict.
#
# Nginx, Apache and uwsgi all attempt to use shared memory mutexes to
# ensure only a single process wakes up when a new connection comes
# in.  Only the process holding the mutex at the time a new
# connections arrives can call accept, and it must release the mutex
# after the accept call concludes.  This also results in a better
# distribution of connections, because the kernel's scheduler
# coordinates fair mutex acquisition.
#
# The downside to this approach is that it requires a reliable shared
# memory mutex, which is unportable and somewhat difficult to manage.
#
# A second approach is have a thread that sleeps on accept(2) that
# pushes accepted connections out to the main event loop.  One reason
# we favor this approach to avoid the difficulties associated with
# shared memory mutexes.
#
# Another is it allows us to immediately accept all incoming
# connections, removing them from the kernel's listen queue and
# placing them instead on in queue we can inspect.  This allows us to
# close connections if we detect our queue has filled up.
#
# This allows us to immediately put back pressure on clients, which
# would not otherwise be able to do.  The reason: on Linux, the listen
# queue holds *completely established* connections -- meaning the
# kernel will complete the three-way handshake prior to our calling
# accept (man 2 listen).  Under very high loads, when no worker is
# able to call accept, connections will languish in the queue until
# they timeout.  By accepting each connection as soon as possible and
# closing it if the queue is full, we're able to communicate capacity
# limitations to clients and log these events.  (Thanks Chris!)
#
# NB: no process synchronizes its user-space queue with any other, so
# it's possible that one slow process will cause dropped connections,
# even though other processes are ready.  Kurt points out that
# determining the likelihood of this is a well understood application
# of queuing theory; it would be good to derive some expression that
# lets us determine probability of dropping connections when at least
# one worker process' queue can accept a new connection.  Until then
# the context variable "accept_queue_maxlen" lets you tweak one of the
# variables.
#
# The actual implementation is somewhat convoluted because of gevent's
# BaseServer -> StreamServer -> WSGIServer inheritance hierarchy:
#
# BaseServer.start -> BaseServer.start_accepting
#                                 |
#                                 v
#                      watcher = loop.io(listening_socket)
#                      watcher.start(self._do_read)
#                                 |
#                                 | (read event)
# BaseServer._do_read <-----------+
#         |
#         | (do_read *only* defined in subclasses)
#         v
#       args <--------- StreamServer.do_read ---- listener.accept()
#       ...
#       WSGIServer.do_handle(*args)  # *only* defined in subclasses
#
# The crux of our implementation is a ThreadWatcher which replaces the
# loop.io(...) instance.  A subclass on threading.Thread, it
# encapsulates:

# 1) a queue bounded by maxlen (a deque, which has fast, thread-safe
#    LIFO operations);
#
# 2) a gevent.event.Event
#
# 3) an async watcher whose send() callback is to release the set the
#    event (2)
#
# 4) a consumer greenlet that wait()s the event (2), checks that
#    there's something in the queue, and *fairly* runs the supplied
#    callback until the queue is empty;
#
# 5) a run() method that blocks until listener.accept(2) returns and
#     a) pushes the resulting socket and address *or* exception onto the
#        queue
#
#     b) calls the async watcher's (3) send method
#
# Putting this together:
#
#         ThreadWatcher       |         main thread
# ----------------------------+-------------------------------
#                             | 4. event.set()    <----------+
#                             |                              |
#                             |       +-----------------+    |
#  1. sock, addr = accept(2)  |       | waiter_greenlet |    |
#                             |       +-----------------+    |
#                             |       |                 |    |
#     push                  queue     | 5. event.wait() |    |
#     sock, addr  +-------------------+---+             |    |
#  2. onto     -> |          (sock, addr) |             |    |
#     queue;      +-------------------+---+             |    |
#                             |       | 6. while queue: |    |
#                             |       |     callback()  |    |
#                             |       |     sleep(0)    |    |
#  3. async.send()            |       |                 |    |
#            |                |       +-----------------+    |
#            |                |                              |
#            +-----------------------------------------------+
#                             |
#
# So ThreadWatcher requires that it's the only writer to the queue,
# and waiter_greenlet in the main thread requires that it's the only
# consumer of the queue.
#
# However, nothing in the above description consumes off the queue!
# Because of the code flow shown in the topmost diagram, we have to
# replace StreamServer with an implementation that knows that
# start_accepting() means create and spin up a ThreadWatcher, and
# do_read() means to pop off the queue.  So the new code flow is as
# follows:
#
# BaseServer.start -> ThreadQueueServer.start_accepting
#                                 |
#                                 v
#                      watcher = ThreadWatcher(listening_socket)
#                      watcher.start(callback=self._do_read)
#                                 |
#                                 | (async.send() fires callback)
# BaseServer._do_read <-----------+
#         |
#         | (do_read *only* defined in subclasses)
#         v
#       args <--------- ThreadQueueServer.do_read ---- queue.popleft()
#       ....
#       ThreadQueueWSGIServer.do_handle(*args)  # *only* defined in subclasses
#
#
# The queue depth can be controlled via Context.accept_queue_maxlen
#
# Finally: we define a ThreadQueueWSGIServer that inherits from
# pywsgi.WSGIServer and our ThreadQueueServer *in that order*.
# Python's C3 MRO algorithm ensures that pywsgi.WSGIServer calls
# ThreadQueueServer's start_accepting, not StreamServer or BaseServer's


DROPPED_CONN_STATS = 'server_group.dropped_connections.queue_full'
DROPPED_EXC_STATS = 'server_group.dropped_exceptions.queue_full'


class ThreadWatcher(threading.Thread):

    def __init__(self, listener, loop, maxlen=128):
        super(ThreadWatcher, self).__init__()
        # TODO: explicit join!!
        self.daemon = True
        self.maxlen = maxlen
        self.queue = collections.deque(maxlen=maxlen)

        self.listener = listener
        # the event our watcher greenlet wait()s on.
        self.event = gevent.event.Event()
        # a cross-thread way to invoke event.set
        self.async = loop.async()
        self.running = False

    def _make_waiter(self, callback):
        # the watcher greenlet
        def waiter():
            while self.running:
                ml.ld('Thread connection consumer greenlet waiting')
                ml2.info('thread_consumer').success('waiting')
                self.event.clear()
                self.event.wait()
                ml2.info('thread_consumer').success('woke up')
                ml.ld('Thread connection consumer greenlet woke up')

                while self.queue and self.running:
                    callback()
                    gevent.sleep(0)

        return waiter

    def start(self, callback):
        self.running = True
        # invoke self.event.set() on async.send().  This is invoked in
        # the *main* thread
        self.async.start(self.event.set)
        self.waiter = gevent.spawn(self._make_waiter(callback))
        super(ThreadWatcher, self).start()

    def stop(self):
        self.running = False
        # wake up the thread and have it bail out
        self.listener.shutdown(socket.SHUT_RDWR)

    def run(self):
        _nanotime = nanotime
        _DROPPED_CONN_STATS = DROPPED_CONN_STATS
        _DROPPED_EXC_STATS = DROPPED_EXC_STATS

        while self.running:
            sock, addr, exc = None, None, None
            try:
                sock, addr = self.listener.accept()
            except socket.error as exc:
                if exc.errno == errno.EINVAL:
                    ml.la('thread accept resulted in EINVAL; '
                          'assuming socket has been shutdown and terminating '
                          'accept loop')
                    self.running = False
                    return
            except Exception as exc:
                # Maybe call sys.exc_info() here?  Is that safe to
                # send across threads?
                pass
            if len(self.queue) >= self.maxlen:
                ctx = context.get_context()
                stats = context.get_context().stats
                log_rec = ctx.log.critical('HTTP')
                if sock and addr:
                    sock.close()
                    stats[_DROPPED_CONN_STATS].add(1)
                    log_rec.failure('thread closed {socket} on {addr} '
                                    'because queue is full',
                                    socket=socket,
                                    addr=addr)
                else:
                    stats[_DROPPED_EXC_STATS].add(1)
                    log_rec.failure('thread dropped {exc} '
                                    'because queue is full',
                                    exc=exc)
            else:
                self.queue.appendleft((sock, addr, exc, _nanotime()))
                # wake up the watcher greenlet in the main thread
                self.async.send()


CONN_AGE_STATS = 'server_group.queued_connection_age_ms'


class ThreadQueueServer(gevent.server.StreamServer):

    def start_accepting(self):
        # NB: This is called via BaseServer.start, which is invoked
        # *only* in post_fork.  It is *criticial* this thread is *not*
        # started prior to forking, lest it die.
        if self._watcher is None:
            accept_maxlen = context.get_context().accept_queue_maxlen
            self._watcher = ThreadWatcher(self.socket, self.loop,
                                          accept_maxlen)
            self._watcher.start(self._do_read)

    def do_read(self):
        # invoked via BaseServer._do_read.  Whereas
        # StreamServer.do_read calls self.socket.accept, we just
        # need to pop off our queue
        if not self._watcher:
            return
        if not self._watcher.queue:
            raise RuntimeError('QUEUE DISAPPEARED')
        client_socket, address, exc, pushed_at = self._watcher.queue.pop()

        age = nanotime() - pushed_at
        context.get_context().stats[CONN_AGE_STATS].add(age / 1e6)

        if exc is not None:
            # raise the Exception
            raise exc

        return gevent.socket.socket(_sock=client_socket), address

# don't use the thread queue server if we're not going to fork
if ufork:
    class ThreadQueueWSGIServer(pywsgi.WSGIServer, ThreadQueueServer):
        pass
else:
    ThreadQueueWSGIServer = pywsgi.WSGIServer


class SslContextWSGIServer(ThreadQueueWSGIServer):
    handler_class = MakeFileCloseWSGIHandler

    @async.timed
    def wrap_socket_and_handle(self, client_socket, address):
        ctx = context.get_context()
        ctx.client_sockets[client_socket] = 1

        if not self.ssl_args:
            raise ValueError('https server requires server-side'
                             ' SSL certificate')
        protocol = _socket_protocol(client_socket)
        if protocol == "ssl":
            with ctx.log.info('HANDLE.SSL', str(address[0])):
                ssl_socket = async.wrap_socket_context(
                    client_socket, **self.ssl_args)
            ctx.sketches['http.ssl.client_ips'].add(address[0])
            return self.handle(ssl_socket, address)
        elif protocol == "http":
            with ctx.log.info('HANDLE.NOSSL', str(address[0])):
                self._no_ssl(client_socket, address)
            ctx.sketches['http.client_ips'].add(address[0])
        else:
            context.get_context().intervals["server.pings"].tick()

    def _no_ssl(self, client_socket, address):
        'externalizes no-SSL behavior so MultiProtocolWSGIServer can override'
        client_socket.send(_NO_SSL_HTTP_RESPONSE)
        async.killsock(client_socket)


class MultiProtocolWSGIServer(SslContextWSGIServer):
    def _no_ssl(self, client_socket, address):
        return self.handle(client_socket, address)


# http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
_HTTP_METHODS = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTION',
                 'CONNECT', 'PATCH')

_SSL_RECORD_TYPES = {
    '\x14': 'CHANGE_CIPHER_SPEC',
    '\x15': 'ALERT',
    '\x16': 'HANDSHAKE',
    '\x17': 'APPLICATION_DATA'}

_SSL_VERSIONS = {
    '\x03\x00': 'SSL3',
    '\x03\x01': 'TLS1',
    '\x03\x02': 'TLS1.1',
    '\x03\x03': 'TLS1.2'}


_NO_SSL_HTTP_RESPONSE = "\r\n".join([
    'HTTP/1.1 401 UNAUTHORIZED',
    'Content-Type: text/plain',
    'Content-Length: ' + str(len('SSL REQUIRED')),
    '',
    'SSL REQUIRED'])


def _socket_protocol(client_socket):
    first_bytes = client_socket.recv(10, socket.MSG_PEEK)
    if any([method in first_bytes for method in _HTTP_METHODS]):
        return "http"
    elif not first_bytes:
        # TODO: empty requests are sometimes sent ([socket] keepalives?)
        return
    elif first_bytes[0] in _SSL_RECORD_TYPES and first_bytes[1:3] in _SSL_VERSIONS:
        return "ssl"
    else:
        raise IOError("unrecognized client protocol: {0!r}".format(first_bytes))


class RotatingGeventLog(object):
    def __init__(self, size=10000):
        self.msgs = collections.deque()
        self.size = size

    def write(self, msg):
        self.msgs.appendleft(msg)
        if len(self.msgs) > self.size:
            self.msgs.pop()


# a little helper for running an interactive console over a socket
import code
import sys


class SockConsole(code.InteractiveConsole):
    def __init__(self, sock):
        code.InteractiveConsole.__init__(self)
        self.sock = sock
        self.sock_file = sock.makefile()

    def write(self, data):
        self.sock.sendall(data)

    def raw_input(self, prompt=""):
        self.write(prompt)
        inp = self.sock_file.readline()
        if inp == "":
            raise OSError("client socket closed")
        inp = inp[:-1]
        return inp

    def _display_hook(self, obj):
        '''
        Handle an item returned from the exec statement.
        '''
        self._last = ""
        if obj is None:
            return
        self.locals['_'] = None
        # clean up output by adding \n here; so you don't see "hello world!">>>
        # TODO: is there a better way to handle this?
        self._last = repr(obj) + "\n"
        self.locals['_'] = obj

    def runcode(self, _code):
        '''
        Wraps base runcode to put displayhook around it.
        TODO: add a new displayhook dispatcher so that the
        current SockConsole is a greenlet-tree local.
        (In case the statement being executed itself
        causes greenlet switches.)
        '''
        prev = sys.displayhook
        sys.displayhook = self._display_hook
        self._last = None
        code.InteractiveConsole.runcode(self, _code)
        sys.displayhook = prev
        if self._last is not None:
            self.write(self._last)


def console_sock_handle(sock, address):
    console = SockConsole(sock)
    console.interact("Connected to pid {0} from {1}...".format(
        os.getpid(), address))


# TODO: move elsewhere

class SimpleLogMiddleware(clastic.Middleware):
    provides = ['api_cal_trans']

    def request(self, next, request, _route):
        url = getattr(_route, 'pattern', '').encode('utf-8')
        ctx = context.get_context()
        with ctx.log.info('URL', url) as request_txn:
            request_txn.msg = {}
            return next(api_cal_trans=request_txn)
