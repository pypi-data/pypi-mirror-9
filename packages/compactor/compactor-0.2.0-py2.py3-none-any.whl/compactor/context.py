import logging
import socket
import threading
import os
try:
    import asyncio
except ImportError:
    import trollius as asyncio

from collections import defaultdict
from functools import partial

from .httpd import HTTPD
from .request import encode_request

from tornado import stack_context
from tornado.iostream import IOStream
from tornado.netutil import bind_sockets
from tornado.platform.asyncio import BaseAsyncIOLoop

log = logging.getLogger(__name__)


class Context(threading.Thread):
  class Error(Exception): pass
  class SocketError(Error): pass
  class InvalidProcess(Error): pass
  class InvalidMethod(Error): pass

  _SINGLETON = None
  _LOCK = threading.Lock()

  CONNECT_TIMEOUT_SECS = 5

  @classmethod
  def make_socket(cls, ip, port):
    """Bind to a new socket.

    If LIBPROCESS_PORT or LIBPROCESS_IP are configured in the environment,
    these will be used for socket connectivity.
    """
    bound_socket = bind_sockets(port, address=ip)[0]
    ip, port = bound_socket.getsockname()

    if not ip or ip == '0.0.0.0':
      ip = socket.gethostbyname(socket.gethostname())

    return bound_socket, ip, port

  @classmethod
  def get_ip_port(cls, ip=None, port=None):
    ip = ip or os.environ.get('LIBPROCESS_IP', '0.0.0.0')
    try:
      port = int(port or os.environ.get('LIBPROCESS_PORT', 0))
    except ValueError:
      raise self.Error('Invalid ip/port provided')
    return ip, port

  @classmethod
  def singleton(cls, delegate='', **kw):
    with cls._LOCK:
      if cls._SINGLETON:
        if cls._SINGLETON.delegate != delegate:
          raise RuntimeError('Attempting to construct different singleton context.')
      else:
        cls._SINGLETON = cls(delegate=delegate, **kw)
        cls._SINGLETON.start()
    return cls._SINGLETON

  def __init__(self, delegate='', loop=None, ip=None, port=None):
    self._processes = {}
    self._links = defaultdict(set)
    self.delegate = delegate
    loop = loop or asyncio.new_event_loop()

    class CustomIOLoop(BaseAsyncIOLoop):
      def initialize(self):
        super(CustomIOLoop, self).initialize(loop, close_loop=False)

    self.loop = CustomIOLoop()

    self._ip = None
    ip, port = self.get_ip_port(ip, port)
    sock, self.ip, self.port = self.make_socket(ip, port)
    self.http = HTTPD(sock, self.loop)

    self._connections = {}

    super(Context, self).__init__()
    self.daemon = True
    self.lock = threading.Lock()
    self.__id = 1

  def is_local(self, pid):
    return self.ip == pid.ip and self.port == pid.port

  def assert_local_pid(self, pid):
    if not self.is_local(pid):
      raise self.InvalidProcess('Operation only valid for local processes!')

  def unique_suffix(self):
    with self.lock:
      suffix, self.__id = '(%d)' % self.__id, self.__id + 1
      return suffix

  def run(self):
    # Start the loop for this context, this is a blocking call and will
    # keep the thread alive.
    self.loop.start()
    self.loop.close()

  def stop(self):
    log.debug('Stopping context')

    pids = list(self._processes)

    # Clean up the context
    for pid in pids:
      self.terminate(pid)
    for connection in list(self._connections.values()):
      connection.close()

    self.loop.stop()

  def spawn(self, process):
    process.bind(self)
    process.initialize()
    self.http.mount_process(process)
    self._processes[process.pid] = process
    return process.pid

  def _get_function(self, pid, method):
    try:
      for mailbox, callable in self._processes[pid].iter_handlers():
        if method == mailbox:
          return callable
    except KeyError:
      raise self.InvalidProcess('Unknown process %s' % pid)
    raise self.InvalidMethod('Unknown method %s on %s' % (method, pid))

  def dispatch(self, pid, method, *args):
    self.assert_local_pid(pid)
    function = self._get_function(pid, method)
    self.loop.add_callback(function, *args)

  def delay(self, amount, pid, method, *args):
    self.assert_local_pid(pid)
    function = self._get_function(pid, method)
    self.loop.add_timeout(self.loop.time() + amount, function, *args)

  def maybe_connect(self, to_pid, callback=None):
    """Synchronously open a connection to to_pid or return a connection if it exists."""

    callback = stack_context.wrap(callback or (lambda stream: None))

    def streaming_callback(data):
      # we are not guaranteed to get an acknowledgment, but log and discard bytes if we do.
      log.info('Received %d bytes from %s, discarding.' % (len(data), to_pid))
      log.debug('  data: %r' % (data,))

    def on_connect(exit_cb, stream):
      log.info('Connection to %s established' % to_pid)
      self._connections[to_pid] = stream
      callback(stream)
      self.loop.add_callback(stream.read_until_close, exit_cb,
                             streaming_callback=streaming_callback)

    stream = self._connections.get(to_pid)

    if stream is not None:
      callback(stream)
      return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    if not sock:
      raise self.SocketError('Failed opening socket')

    # Set the socket non-blocking
    sock.setblocking(0)

    stream = IOStream(sock, io_loop=self.loop)
    stream.set_nodelay(True)
    stream.set_close_callback(partial(self.__on_exit, to_pid, b'closed from maybe_connect'))

    connect_callback = partial(on_connect, partial(self.__on_exit, to_pid), stream)

    log.info('Establishing connection to %s' % to_pid)
    stream.connect((to_pid.ip, to_pid.port), callback=connect_callback)
    if stream.closed():
      raise self.SocketError('Failed to initiate stream connection')
    log.info('Maybe connected to %s' % to_pid)

  def send(self, from_pid, to_pid, method, body=None):
    """Send a message method from_pid to_pid with body (optional)"""

    # TODO(wickman) Restore local short-circuiting.
    """
    # short circuit for local processes
    if to_pid in self._processes:
      log.info('Doing local dispatch of %s => %s (method: %s)' % (
               from_pid, to_pid, method))
      self.dispatch(to_pid, method, from_pid, body or b'')
      return
    """

    request_data = encode_request(from_pid, to_pid, method, body=body)

    log.info('Sending POST %s => %s (payload: %d bytes)' % (
             from_pid, to_pid.as_url(method), len(request_data)))

    def on_connect(stream):
      log.info('Writing %s from %s to %s' % (len(request_data), from_pid, to_pid))
      stream.write(request_data)
      log.info('Wrote %s from %s to %s' % (len(request_data), from_pid, to_pid))

    self.maybe_connect(to_pid, on_connect)

  def __erase_link(self, to_pid):
    for pid, links in self._links.items():
      try:
        links.remove(to_pid)
        self._processes[pid].exited(to_pid)
      except KeyError:
        continue

  def __on_exit(self, to_pid, body):
    log.info('Disconnected from %s (%s)', to_pid, body)
    stream = self._connections.pop(to_pid, None)
    if stream is None:
      log.error('Received disconnection from %s but no stream found.' % to_pid)
    self.__erase_link(to_pid)

  def link(self, pid, to):
    def really_link():
      self._links[pid].add(to)
      log.info('Added link from %s to %s' % (pid, to))

    def on_connect(stream):
      really_link()

    if self.is_local(pid):
      really_link()
    else:
      self.maybe_connect(to, on_connect)

  def terminate(self, pid):
    log.info('Terminating %s' % pid)
    process = self._processes.pop(pid, None)
    if process:
      log.info('Unmounting %s' % process)
      self.http.unmount_process(process)
    self.__erase_link(pid)

  def __str__(self):
    return 'Context(%s:%s)' % (self.ip, self.port)
