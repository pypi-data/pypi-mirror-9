#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Netius System
# Copyright (C) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Netius System.
#
# Hive Netius System is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Netius System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Netius System. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import request

from .common import * #@UnusedWildImport

BUFFER_SIZE = None
""" The size of the buffer that is going to be used in the
sending and receiving of packets from the client, this value
may influence performance by a large factor """

GC_TIMEOUT = 30.0
""" The timeout to be used for the running of the garbage
collector of pending request in a datagram client, this
value will be used n the delay operation of the action """

class Client(Base):
    """
    Abstract client implementation, should provide the required
    mechanisms for basic socket client handling and thread starting
    and managing techniques. Proper and concrete implementation for
    the various socket types should inherit from this class.
    """

    _client = None
    """ The global static client meant to be reused by the
    various static clients that may be created, this client
    may leak creating blocking threads that will prevent the
    system from exiting correctly, in order to prevent that
    the cleanup method should be called """

    def __init__(self, thread = True, daemon = False, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        self.receive_buffer = kwargs.get("receive_buffer", BUFFER_SIZE)
        self.send_buffer = kwargs.get("send_buffer", BUFFER_SIZE)
        self.thread = thread
        self.daemon = daemon
        self._thread = None

    def __del__(self):
        Base.__del__(self)
        self.debug("Client (%s) '%s' deleted from memory" % (self.name, self._uuid))

    @classmethod
    def get_client_s(cls, *args, **kwargs):
        if cls._client: return cls._client
        cls._client = cls(*args, **kwargs)
        return cls._client

    @classmethod
    def cleanup_s(cls):
        if not cls._client: return
        cls._client.close()

    def reads(self, reads, state = True):
        if state: self.set_state(STATE_READ)
        for read in reads:
            self.on_read(read)

    def writes(self, writes, state = True):
        if state: self.set_state(STATE_WRITE)
        for write in writes:
            self.on_write(write)

    def errors(self, errors, state = True):
        if state: self.set_state(STATE_ERRROR)
        for error in errors:
            self.on_error(error)

    def ensure_loop(self, env = True):
        """
        Ensures that the proper main loop thread requested in the building
        of the entity is started if that was requested.

        This mechanisms is required because the thread construction and
        starting should be deferred until an operation in the connection
        is requested (lazy thread construction).

        The call to this method should be properly inserted on the code so
        that it is only called when a main (polling) loop is required.

        @type env: bool
        @param env: If the environment variables should be used for the
        setting of some of the parameters of the new client/poll to be used.
        """

        # verifies if the (run in) thread flag is set and that the there's
        # not thread currently created for the client in case any of these
        # conditions fails the control flow is returned immediately to caller
        if not self.thread: return
        if self._thread: return

        # runs the various extra variable initialization taking into
        # account if the environment variable is currently set or not
        # please note that some side effects may arise from this set
        if env: self.level = self.get_env("LEVEL", self.level)
        if env: self.logging = self.get_env("LOGGING", self.logging)
        if env: self.poll_name = self.get_env("POLL", self.poll_name)
        if env: self.poll_timeout = self.get_env(
            "POLL_TIMEOUT",
            self.poll_timeout,
            cast = float
        )

        # in case the thread flag is set a new thread must be constructed
        # for the running of the client's main loop then, these thread
        # may or may not be constructed using a daemon approach
        self._thread = BaseThread(self, daemon = self.daemon)
        self._thread.start()

class DatagramClient(Client):

    def __init__(self, *args, **kwargs):
        Client.__init__(self, *args, **kwargs)
        self.socket = None
        self.renable = True
        self.wready = True
        self.pending_s = 0
        self.pending = []
        self.requests = []
        self.requests_m = {}
        self.pending_lock = threading.RLock()

    def boot(self):
        Client.boot(self)
        self.keep_gc(timeout = GC_TIMEOUT, run = False)

    def cleanup(self):
        Client.cleanup(self)
        del self.requests[:]
        self.requests_m.clear()

    def on_read(self, _socket):
        try:
            # verifies if there's any pending operations in the
            # socket (eg: ssl handshaking) and performs them trying
            # to finish them, if they are still pending at the current
            # state returns immediately (waits for next loop)
            if self._pending(_socket): return

            # iterates continuously trying to read as much data as possible
            # when there's a failure to read more data it should raise an
            # exception that should be handled properly
            while True:
                data, address = _socket.recvfrom(CHUNK_SIZE)
                self.on_data(address, data)
        except ssl.SSLError as error:
            error_v = error.args[0]
            if error_v in SSL_SILENT_ERRORS:
                self.debug(error)
            elif not error_v in SSL_VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
        except socket.error as error:
            error_v = error.args[0]
            if error_v in SILENT_ERRORS:
                self.debug(error)
            elif not error_v in VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
        except BaseException as exception:
            self.warning(exception)
            lines = traceback.format_exc().splitlines()
            for line in lines: self.info(line)

    def on_write(self, _socket):
        try:
            self._send(_socket)
        except ssl.SSLError as error:
            error_v = error.args[0]
            if error_v in SSL_SILENT_ERRORS:
                self.debug(error)
            elif not error_v in SSL_VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
        except socket.error as error:
            error_v = error.args[0]
            if error_v in SILENT_ERRORS:
                self.debug(error)
            elif not error_v in VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
        except BaseException as exception:
            self.warning(exception)
            lines = traceback.format_exc().splitlines()
            for line in lines: self.info(line)

    def on_error(self, _socket):
        pass

    def on_data(self, connection, data):
        pass

    def keep_gc(self, timeout = GC_TIMEOUT, run = True):
        if run: self.gc()
        self.delay(self.keep_gc, timeout)

    def gc(self):
        # in case there're no requests pending in the current client
        # there's no need to start the garbage collection logic, as
        # this would required some (minimal) resources
        if not self.requests: return

        # prints a message (for debug) about the garbage collection
        # operation that is going to be run
        self.debug("Running garbage collection ...")

        # retrieves the current time value and iterates over the
        # various request currently defined in the client (pending
        # and answer) to try to find the ones that have time out
        current = time.time()
        while True:
            # verifies if the requests structure (list) is empty and
            # if that's the case break the loop, nothing more remains
            # to be processed for the current garbage collection operation
            if not self.requests: break

            # retrieves the top level request (peek operation) and
            # verifies if the timeout value of it has exceed the
            # current time if that's the case removes it as it
            # should no longer be handled (time out)
            request = self.requests[0]
            if request.timeout > current: break
            self.remove_request(request)

            # extracts the callback method from the request and in
            # case it is defined and valid calls it with an invalid
            # argument meaning that an error has occurred
            callback = request.callback
            callback and callback(None)

    def add_request(self, request):
        # adds the current request object to the list of requests
        # that are pending a valid response, a garbage collector
        # system should be able to erase this request from the
        # pending list in case a timeout value has passed
        self.requests.append(request)
        self.requests_m[request.id] = request

    def remove_request(self, request):
        self.requests.remove(request)
        del self.requests_m[request.id]

    def get_request(self, id):
        is_response = isinstance(id, request.Response)
        if is_response: id = id.get_id()
        return self.requests_m.get(id, None)

    def ensure_socket(self):
        # in case the socket is already created and valid returns immediately
        # as nothing else remain to be done in the current method
        if self.socket: return

        # prints a small debug message about the udp socket that is going
        # to be created for the client's connection
        self.debug("Creating clients's udp socket ...")

        # creates the socket that it's going to be used for the listening
        # of new connections (client socket) and sets it as non blocking
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)

        # sets the various options in the service socket so that it becomes
        # ready for the operation with the highest possible performance
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # adds the socket to all of the pool lists so that it's ready to read
        # write and handle error, this is the expected behavior of a service
        # socket so that it can handle all of the expected operations
        self.sub_all(self.socket)

    def ensure_write(self):
        # retrieves the identifier of the current thread and
        # checks if it's the same as the one defined in the
        # owner in case it's not then the operation is not
        # considered to be safe and must be delayed
        cthread = threading.current_thread()
        tid = cthread.ident or 0
        is_safe = tid == self.tid

        # in case the thread where this code is being executed
        # is not the same the operation is considered to be not
        # safe and so it must be delayed to be executed in the
        # next loop of the thread cycle, must return immediately
        # to avoid extra subscription operations
        if not is_safe: self.delay(self.ensure_write); return

        # adds the current socket to the list of write operations
        # so that it's going to be available for writing as soon
        # as possible from the poll mechanism
        self.sub_write(self.socket)

    def remove_write(self):
        self.unsub_write(self.socket)

    def enable_read(self):
        if not self.renable == False: return
        self.renable = True
        self.sub_read(self.socket)

    def disable_read(self):
        if not self.renable == True: return
        self.renable = False
        self.unsub_read(self.socket)

    def send(self, data, address, delay = False, callback = None):
        self.ensure_loop()

        data = legacy.bytes(data)
        data_l = len(data)

        if callback: data = (data, callback)
        data = (data, address)

        cthread = threading.current_thread()
        tid = cthread.ident or 0
        is_safe = tid == self.tid

        self.pending_lock.acquire()
        try: self.pending.insert(0, data)
        finally: self.pending_lock.release()

        self.pending_s += data_l

        if self.wready:
            if is_safe and not delay: self._flush_write()
            else: self.delay(self._flush_write, verify = True)
        else:
            self.ensure_write()

    def _send(self, _socket):
        self.wready = True
        self.pending_lock.acquire()
        try:
            while True:
                if not self.pending: break
                data = self.pending.pop()
                data_o = data
                callback = None
                data, address = data
                is_tuple = type(data) == tuple
                if is_tuple: data, callback = data
                data_l = len(data)

                try:
                    # tries to send the data through the socket and
                    # retrieves the number of bytes that were correctly
                    # sent through the socket, this number may not be
                    # the same as the size of the data in case only
                    # part of the data has been sent
                    if data: count = _socket.sendto(data, address)
                    else: count = 0
                except:
                    # sets the current connection write ready flag to false
                    # so that a new level notification must be received
                    self.wready = False

                    # ensures that the write event is going to be triggered
                    # this is required so that the remaining pending data is
                    # going to be correctly written on a new write event,
                    # triggered when the connection is ready for more writing
                    self.ensure_write()

                    # in case there's an exception must add the data
                    # object to the list of pending data because the data
                    # has not been correctly sent
                    self.pending.append(data_o)
                    raise
                else:
                    # decrements the size of the pending buffer by the number
                    # of bytes that were correctly send through the buffer
                    self.pending_s -= count

                    # verifies if the data has been correctly sent through
                    # the socket and for suck situations calls the callback
                    # object, otherwise creates a new data object with only
                    # the remaining (partial data) and the callback to be
                    # sent latter (only then the callback is called)
                    is_valid = count == data_l
                    if is_valid:
                        callback and callback(self)
                    else:
                        data_o = ((data[count:], callback), address)
                        self.pending.append(data_o)
        finally:
            self.pending_lock.release()

        self.remove_write()

    def _flush_write(self):
        """
        Flush operations to be called by the delaying controller
        (in ticks) that will trigger all the write operations
        pending for the current connection's socket.
        """

        self.ensure_socket()
        self.writes((self.socket,), state = False)

class StreamClient(Client):

    def __init__(self, *args, **kwargs):
        Client.__init__(self, *args, **kwargs)
        self.pendings = []
        self.free_map = {}
        self._pending_lock = threading.RLock()

    def ticks(self):
        self.set_state(STATE_TICK)
        self._lid = (self._lid + 1) % 2147483647
        if self.pendings: self._connects()
        self._delays()

    def acquire_c(
        self,
        host,
        port,
        ssl = False,
        key_file = None,
        cer_file = None,
        callback = None
    ):
        # creates the tuple that is going to describe the connection
        # and tries to retrieve a valid connection from the map of
        # free connections (connection re-usage)
        connection_t = (host, port, ssl, key_file, cer_file)
        connection_l = self.free_map.get(connection_t, None)

        # in case the connection list was successfully retrieved a new
        # connection is re-used by acquiring the connection
        if connection_l:
            connection = connection_l.pop()
            self.acquire(connection)

        # otherwise a new connection must be created by establishing
        # a connection operation, this operation is not going to be
        # performed immediately as it's going to be deferred to the
        # next execution cycle (delayed execution)
        else:
            connection = self.connect(
                host,
                port,
                ssl = ssl,
                key_file = key_file,
                cer_file = cer_file
            )
            connection.tuple = connection_t

        # returns the connection object the caller method, this connection
        # is acquired and should be safe and ready to be used
        return connection

    def release_c(self, connection):
        if not hasattr(connection, "tuple"): return
        connection_t = connection.tuple
        connection_l = self.free_map.get(connection_t, [])
        connection_l.append(connection)
        self.free_map[connection_t] = connection_l
        self.on_release(connection)

    def remove_c(self, connection):
        if not hasattr(connection, "tuple"): return
        connection_t = connection.tuple
        connection_l = self.free_map.get(connection_t, [])
        if connection in connection_l: connection_l.remove(connection)

    def connect(
        self,
        host,
        port,
        ssl = False,
        key_file = None,
        cer_file = None,
        family = socket.AF_INET,
        type = socket.SOCK_STREAM
    ):
        if not host: raise errors.NetiusError("Invalid host for connect operation")
        if not port: raise errors.NetiusError("Invalid port for connect operation")

        # ensures that a proper loop cycle is available for the current
        # client, otherwise the connection operation would become stalled
        # because there's no listening of events for it
        self.ensure_loop()

        # ensures that the proper socket family is defined in case the
        # requested host value is unix socket oriented, this step greatly
        # simplifies the process of created unix socket based clients
        family = socket.AF_UNIX if host == "unix" else family

        # verifies the kind of socket that is going to be used for the
        # connect operation that is going to be performed, note that the
        # unix type should be used with case as it does not exist in every
        # operative system and may raised an undefined exceptions
        is_unix = hasattr(socket, "AF_UNIX") and family == socket.AF_UNIX
        is_inet = family in (socket.AF_INET, socket.AF_INET6)

        key_file = key_file or SSL_KEY_PATH
        cer_file = cer_file or SSL_CER_PATH

        _socket = socket.socket(family, type)
        _socket.setblocking(0)

        if ssl: _socket = self._ssl_wrap(
            _socket,
            key_file = key_file,
            cer_file = cer_file,
            server = False
        )

        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if is_inet: _socket.setsockopt(
            socket.IPPROTO_TCP,
            socket.TCP_NODELAY,
            1
        )
        if self.receive_buffer: _socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_RCVBUF,
            self.receive_buffer
        )
        if self.send_buffer: _socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_SNDBUF,
            self.send_buffer
        )
        self._socket_keepalive(_socket)

        address = port if is_unix else (host, port)
        connection = self.new_connection(_socket, address, ssl = ssl)

        self._pending_lock.acquire()
        try: self.pendings.append(connection)
        finally: self._pending_lock.release()

        return connection

    def acquire(self, connection):
        acquire = lambda: self.on_acquire(connection)
        self.delay(acquire)

    def on_read(self, _socket):
        # retrieves the connection object associated with the
        # current socket that is going to be read in case there's
        # no connection available or the status is not open
        # must return the control flow immediately to the caller
        connection = self.connections_m.get(_socket, None)
        if not connection: return
        if not connection.status == OPEN: return
        if not connection.renable == True: return

        try:
            # in case the connection is under the connecting state
            # the socket must be verified for errors and in case
            # there's none the connection must proceed, for example
            # the ssl connection handshake must be performed/retried
            if connection.connecting: self._connectf(connection)

            # if the current connection state is upgrading the proper
            # upgrading operations must be performed for example ssl
            # handshaking and then the proper callbacks may be called
            # as a consequence of that, note that if there's pending
            # operations at the end of this call no data will be received
            # and processed as a consequence
            if connection.upgrading: self._upgradef(connection)

            # verifies if there's any pending operations in the
            # socket (eg: ssl handshaking) and performs them trying
            # to finish them, if they are still pending at the current
            # state returns immediately (waits for next loop)
            if self._pending(_socket): return

            # iterates continuously trying to read as much data as possible
            # when there's a failure to read more data it should raise an
            # exception that should be handled properly
            while True:
                data = _socket.recv(CHUNK_SIZE)
                if data: self.on_data(connection, data)
                else: connection.close(); break
                if not connection.status == OPEN: break
                if not connection.renable == True: break
                if not connection.socket == _socket: break
        except ssl.SSLError as error:
            error_v = error.args[0]
            if error_v in SSL_SILENT_ERRORS:
                self.debug(error)
                connection.close()
            elif not error_v in SSL_VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
                connection.close()
        except socket.error as error:
            error_v = error.args[0]
            if error_v in SILENT_ERRORS:
                self.debug(error)
                connection.close()
            elif not error_v in VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
                connection.close()
        except BaseException as exception:
            self.warning(exception)
            lines = traceback.format_exc().splitlines()
            for line in lines: self.info(line)
            connection.close()

    def on_write(self, _socket):
        # retrieves the connection associated with the socket that
        # is ready for the write operation and verifies that it
        # exists and the current status of it is open (required)
        connection = self.connections_m.get(_socket, None)
        if not connection: return
        if not connection.status == OPEN: return

        # in case the connection is under the connecting state
        # the socket must be verified for errors and in case
        # there's none the connection must proceed, for example
        # the ssl connection handshake must be performed/retried
        if connection.connecting: self._connectf(connection)

        try:
            connection._send()
        except ssl.SSLError as error:
            error_v = error.args[0]
            if error_v in SSL_SILENT_ERRORS:
                self.debug(error)
                connection.close()
            elif not error_v in SSL_VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
                connection.close()
        except socket.error as error:
            error_v = error.args[0]
            if error_v in SILENT_ERRORS:
                self.debug(error)
                connection.close()
            elif not error_v in VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
                connection.close()
        except BaseException as exception:
            self.warning(exception)
            lines = traceback.format_exc().splitlines()
            for line in lines: self.info(line)
            connection.close()

    def on_error(self, _socket):
        connection = self.connections_m.get(_socket, None)
        if not connection: return
        if not connection.status == OPEN: return

        connection.close()

    def on_connect(self, connection):
        connection.set_connected()
        if hasattr(connection, "tuple"):
            self.on_acquire(connection)

    def on_upgrade(self, connection):
        connection.set_upgraded()

    def on_acquire(self, connection):
        pass

    def on_release(self, connection):
        pass

    def on_data(self, connection, data):
        pass

    def _connectf(self, connection):
        """
        Finishes the process of connecting to the remote end-point
        this should be done in certain steps of the connection.

        The process of finishing the connecting process should include
        the ssl handshaking process.

        @type connection: Connection
        @param connection: The connection that should have the connect
        process tested for finishing.
        """

        error = connection.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if error: self.on_error(connection.socket); return

        if connection.ssl: self._ssl_handshake(connection.socket)
        else: self.on_connect(connection)

    def _upgradef(self, connection):
        self._ssl_handshake(connection.socket)

    def _connects(self):
        self._pending_lock.acquire()
        try:
            while self.pendings:
                connection = self.pendings.pop()
                self._connect(connection)
        finally:
            self._pending_lock.release()

    def _connect(self, connection):
        # in case the current connection has been closed meanwhile
        # the current connection is meant to be avoided and so the
        # method must return immediately to the caller method
        if connection.status == CLOSED: return

        # retrieves the socket associated with the connection
        # and calls the open method of the connection to proceed
        # with the correct operations for the connection
        _socket = connection.socket
        connection.open(connect = True)

        # tries to run the non blocking connection it should
        # fail and the connection should only be considered as
        # open when a write event is raised for the connection
        try: _socket.connect(connection.address)
        except ssl.SSLError as error:
            error_v = error.args[0]
            if not error_v in SSL_VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
                self.trigger("error", self, connection, error)
                connection.close()
                return
        except socket.error as error:
            error_v = error.args[0]
            if not error_v in VALID_ERRORS:
                self.warning(error)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.info(line)
                self.trigger("error", self, connection, error)
                connection.close()
                return
        except BaseException as exception:
            self.warning(exception)
            lines = traceback.format_exc().splitlines()
            for line in lines: self.info(line)
            self.trigger("error", self, connection, exception)
            connection.close()
            raise
        else:
            self._connectf(connection)

        # in case the connection is not of type ssl the method
        # may returns as there's nothing left to be done, as the
        # rest of the method is dedicated to ssl tricks
        if not connection.ssl: return

        # verifies if the current ssl object is a context oriented one
        # (newest versions) or a legacy oriented one, that does not uses
        # any kind of context object, this is relevant in order to make
        # decisions on how the ssl object may be re-constructed
        has_context = hasattr(_socket, "context")
        has_sock = hasattr(_socket, "_sock")

        # creates the ssl object for the socket as it may have been
        # destroyed by the underlying ssl library (as an error) because
        # the socket is of type non blocking and raises an error, note
        # that the creation of the socket varies between ssl versions
        if _socket._sslobj: return
        if has_context: _socket._sslobj = _socket.context._wrap_socket(
            _socket,
            _socket.server_side,
            _socket.server_hostname
        )
        else: _socket._sslobj = ssl._ssl.sslwrap(
            _socket._sock if has_sock else _socket,
            False,
            _socket.keyfile,
            _socket.certfile,
            _socket.cert_reqs,
            _socket.ssl_version,
            _socket.ca_certs
        )

    def _ssl_handshake(self, _socket):
        Client._ssl_handshake(self, _socket)

        # verifies if the socket still has operations pending,
        # meaning that the handshake is still pending data and
        # if that's the case returns immediately (nothing done)
        if _socket._pending: return

        # prints a debug information notifying the developer about
        # the finishing of the handshaking process for the connection
        self.debug("Handshaking completed for socket")

        # tries to retrieve the connection associated with the
        # ssl socket and in case none is available returns
        # immediately as there's nothing to be done here
        connection = self.connections_m.get(_socket, None)
        if not connection: return

        # verifies if the connection is either connecting or upgrading
        # and calls the proper event handler for each event, this is
        # required because the connection workflow is probably dependent
        # on the calling of these event handlers to proceed
        if connection.connecting: self.on_connect(connection)
        elif connection.upgrading: self.on_upgrade(connection)
