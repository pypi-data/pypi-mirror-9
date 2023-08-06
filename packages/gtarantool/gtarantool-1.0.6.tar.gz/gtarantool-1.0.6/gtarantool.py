# -*- coding: utf-8 -*-

import gevent
import gevent.lock
import gevent.socket as socket
from gevent.event import AsyncResult, Event

import errno
import msgpack
import base64

import tarantool
from tarantool.response import Response
from tarantool.request import Request

from tarantool.error import (
    NetworkError,
    DatabaseError,
    warn,
    RetryWarning)

from tarantool.const import (
    SOCKET_TIMEOUT,
    RETRY_MAX_ATTEMPTS,
    RECONNECT_MAX_ATTEMPTS,
    RECONNECT_DELAY,
    IPROTO_GREETING_SIZE)


def connect(host="localhost", port=3301, user=None, password=None):
    return GConnection(host, port,
                       user=user,
                       password=password,
                       socket_timeout=SOCKET_TIMEOUT,
                       reconnect_max_attempts=RECONNECT_MAX_ATTEMPTS,
                       reconnect_delay=RECONNECT_DELAY,
                       connect_now=True)


class GConnection(tarantool.Connection):
    def __init__(self, *args, **kwargs):
        self.lock = gevent.lock.Semaphore()
        self._reader = None
        self._writer = None
        self._write_buffer = b""
        self._write_event = Event()
        self._auth_event = Event()
        self.req_num = 0
        self.req_event = {}
        self.gbuf_size = kwargs.pop("gbuf_size", 16384)

        assert isinstance(self.gbuf_size, int);

        super(GConnection, self).__init__(*args, **kwargs)

        self.error = False  # important not raise exception in response reader

    def generate_sync(self):
        self.req_num += 1
        if self.req_num > 10000000:
            self.req_num = 0

        self.req_event[self.req_num] = AsyncResult()
        return self.req_num

    def close(self):
        if not self.connected:
            return

        self.connected = False
        super(GConnection, self).close()

    def connect(self):
        if self.connected:
            return

        with self.lock:
            if self.connected:
                return

            # duplicate tarantool connect vs gevent monkey patch
            self.connected = False
            try:
                if self._socket:
                    self._socket.close()

                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
                self._socket.connect((self.host, self.port))
                self._socket.settimeout(self.socket_timeout)
                self.connected = True
            except socket.error as ex:
                raise NetworkError(ex)

            # separate gevent thread for write request to tarantool socket
            if self._writer and not self._writer.ready():
                self._writer.kill()

            self._writer = gevent.spawn(self.request_writer)

            # separate gevent thread for read response from tarantool socket
            if self._reader and not self._reader.ready():
                self._reader.kill()

            self._reader = gevent.spawn(self.response_reader)

            self._write_buffer = b""

            if self.user:
                self._auth_event.wait()
                self.authenticate(self.user, self.password)

    def request_writer(self):
        try:
            while self.connected:
                self._write_event.wait()

                while len(self._write_buffer) > 0 and self.connected:
                    sent = self._socket.send(self._write_buffer)
                    self._write_buffer = self._write_buffer[sent:]

                self._write_event.clear()
        except socket.error, ex:
            if self._reader and not self._reader.ready():
                self._reader.kill()

            with self.lock:
                self.close()

                for event in self.req_event.values():
                    event.set(("", ex))

    def response_reader(self):
        try:
            # need handshake here
            greeting = self._socket.recv(IPROTO_GREETING_SIZE)
            self._salt = base64.decodestring(greeting[64:])[:20]
            self._auth_event.set()

            buf = b""
            while self.connected:
                # chunk socket read
                tmp_buf = self._socket.recv(self.gbuf_size)
                if not tmp_buf:
                    raise NetworkError(socket.error(errno.ECONNRESET, "Lost connection to server during query"))

                buf += tmp_buf
                len_buf = len(buf)
                curr = 0

                while len_buf - curr >= 5:
                    length_pack = buf[curr:curr + 5]
                    length = msgpack.unpackb(length_pack)

                    if len_buf - curr < 5 + length:
                        break

                    body = buf[curr + 5:curr + 5 + length]
                    curr += 5 + length

                    response = Response(self, body)  # unpack response

                    # set AsyncResult
                    sync = response.sync
                    if sync in self.req_event:
                        self.req_event[sync].set((response, None))

                # one cut for buffer
                if curr:
                    buf = buf[curr:]
        except socket.error, ex:
            if self._writer and not self._writer.ready():
                self._writer.kill()

            with self.lock:
                self.close()

                for event in self.req_event.values():
                    event.set((None, ex))

    def _send_request(self, request):
        assert isinstance(request, Request)

        if not self.connected:
            self.connect()

        for attempt in xrange(RETRY_MAX_ATTEMPTS):
            self._write_buffer += bytes(request)
            self._write_event.set()

            # read response
            sync = request.sync
            response, ex = self.req_event[sync].get()
            del self.req_event[sync]

            if ex is not None:
                raise ex

            if response.completion_status != 1:
                if response.return_code != 0:
                    raise DatabaseError(response.return_code, response.return_message)

                return response

            warn(response.return_message, RetryWarning)

        # Raise an error if the maximum number of attempts have been made
        raise DatabaseError(response.return_code, response.return_message)
