#!/usr/bin/env python3

# The MIT License (MIT)
# 
# Copyright (c) 2013-2015 Benedikt Schmitt
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
This module contains a high-level API for the TeamSpeak 3 Server Query.
"""


# Modules
# ------------------------------------------------
import re
import time
import socket
import telnetlib
import logging
import threading

# third party
import blinker

# local
try:
    from commands import TS3Commands
    from common import TS3Error
    from escape import TS3Escape
    from response import TS3Response, TS3QueryResponse, TS3Event
    import _lib
except ImportError:
    from .commands import TS3Commands
    from .common import TS3Error
    from .escape import TS3Escape
    from .response import TS3Response, TS3QueryResponse, TS3Event
    from . import _lib


# Backward compatibility
# ------------------------------------------------
try:
    TimeoutError
except NameError:
    TimeoutError = OSError
    

# Data
# ------------------------------------------------
__all__ = [
    "TS3QueryError",
    "TS3ResponseRecvError",
    "TS3BaseConnection",
    "TS3Connection"]

_logger = logging.getLogger(__name__)


# Exceptions
# ------------------------------------------------
class TS3QueryError(TS3Error):
    """
    Raised, if the error code of the response was not 0.
    """

    def __init__(self, resp):
        #: The :class:`TS3Response` instance with the response data.
        self.resp = resp
        return None

    def __str__(self):
        tmp = "error id {}: {}".format(
            self.resp.error["id"], self.resp.error["msg"])
        return tmp


class TS3ResponseRecvError(TS3Error, TimeoutError):
    """
    Raised, if a response could not be received due to a *timeout* or
    if the receive progress has been *canceled* by another thread.
    """

    def __str__(self):
        tmp = "Could not receive the response from the server."
        return tmp
    

# Classes
# ------------------------------------------------
class TS3BaseConnection(object):
    """
    The TS3 query client.

    This class provides only the methods to **handle** the connection to a
    TeamSpeak 3 Server. For a more convenient interface, use the
    :class:`TS3Connection` class.

    Note, that this class supports the ``with`` statement:

        >>> with TS3BaseConnection() as ts3conn:
        ...     ts3conn.open("localhost")
        ...     ts3conn.send(...)
        >>> # This is equal too:
        >>> ts3conn = TS3BaseConnection()
        >>> try:
        ...     ts3conn.open("localhost")
        ...     ts3conn.send(...)
        ... finally:
        ...     ts3conn.close()
    """
   
    def __init__(self, host=None, port=10011):
        """
        If *host* is provided, the connection will be established before
        the constructor returns.

        .. seealso:: :meth:`open`
        """
        # None, if the client is not connected.
        self._telnet_conn = None

        # The last query id, that has been given.
        self._query_counter = 0
        
        # The last query id, that has been fetched.
        self._query_id = 0

        # Maps the query id to the response.
        # query id => TS3Response
        self._responses = dict()

        # Set to true, if a new response has been received.
        self._new_response_event = threading.Condition()

        # Avoid sending data to the same time.
        self._send_lock = threading.Lock()

        # Needed to store a link to the keep alive thread
        # and information about the keep alive intervall.
        self._keepalive_timer = None
        self._keepalive_interval = None

        # To stop the receive progress, if we are waiting for events from
        # another thread.
        self._stop_event = threading.Event()
        self._waiting_for_stop = False
        self._is_listening = False

        # Dispatches all received events in another thread to avoid
        # dead locks.
        # The dispatcher is started, as soon as the first event
        # is received and stopped, when the connection is closed.
        self.__event_dispatcher = _lib.SignalDispatcher()
        
        if host is not None:
            self.open(host, port)
        return None

    # *Simple* get and set methods
    # ------------------------------------------------

    @property
    def telnet_conn(self):
        """
        :getter:
            If the client is connected, the used Telnet instance
            else None.
        :type:
            None or :class:`telnetlib.Telnet`.
        """
        return self._telnet_conn

    def is_connected(self):
        """
        :return:
            True, if the client is currently connected.
        :rtype:
            bool
        """
        return self._telnet_conn is not None
        
    @property
    def last_resp(self):
        """
        :getter:
            The last received response.
        :type:
            :class:`~response.TS3Response`

        :raises LookupError:
            If no response has been received yet.
        """
        # Get the responses with the highest query id in the response
        # dictionary.
        try:
            tmp = max(self._responses)
        except ValueError:
            raise LookupError()
        else:
            return self._responses[tmp]

    def remaining_responses(self):
        """
        :return:
            The number of unfetched responses.
        :type:
            int
        """
        return self._query_counter - self._query_id
        
    # Networking
    # ------------------------------------------------
    
    def open(self, host, port=10011,
             timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Connect to the TS3 Server listening on the address given by the
        *host* and *port* parmeters. If *timeout* is provided, this is the
        maximum time in seconds for the connection attempt.

        :raises OSError:
            If the client is already connected.
        :raises TimeoutError:
            If the connection can not be created.
        """
        if self.is_connected():
             raise OSError("The client is already connected.") 
        else:
            self._query_counter = 0
            self._query_id = 0
            self._responses = dict()

            self._telnet_conn = telnetlib.Telnet(host, port, timeout)            
            # Wait for the first and the second greeting:
            # b'TS3\n\r'
            # b'Welcome to the [...] on a specific command.\n\r'
            self._telnet_conn.read_until(b"\n\r")
            self._telnet_conn.read_until(b"\n\r")

            _logger.info("Created connection to {}:{}.".format(host, port))
        return None

    def close(self):
        """
        Sends the ``quit`` command and closes the telnet connection.

        If you are receiving data from another thread, this method will
        call :meth:`stop_recv` and therefore block, until the the receive
        thread stopped.
        """
        if self.is_connected():
            try:
                # We need to send the quit command directly to avoid
                # dead locks.
                self._telnet_conn.write(b"quit\n\r")
            finally:
                self.stop_recv()
                self.cancel_keepalive()
                self._telnet_conn.close()
                self._telnet_conn = None                
                _logger.debug("Disconnected client.")
        return None

    def fileno(self):
        """
        :return:
            The fileno() of the socket object used internally.
        :rtype:
            int
        """
        return self._telnet_conn.fileno()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
        return None

    def __del__(self):
        self.close()
        return None

    # Keep alive
    # -------------------------
    
    def __send_keepalive_beacon(self):
        """
        Sends the keep alive beacon ``\n\r`` to the server and restarts the
        keep alive timer :attr:`_keepalive_timer`.

        .. seealso::

            * :meth:`cancel_keepalive`
            * :meth:`keepalive`
        """        
        # Send the beacon.
        with self._send_lock:
            self._telnet_conn.write(b"\n\r")

        # Restart the timer.
        if self._keepalive_timer is not None:
            self._keepalive_timer.cancel()
            self._keepalive_timer = None

        if self._keepalive_interval is not None:            
            self._keepalive_timer = threading.Timer(
                interval = self._keepalive_interval,
                function = self.__send_keepalive_beacon
                )
            self._keepalive_timer.start()
        return None

    def cancel_keepalive(self):
        """
        Cancels the *keepalive* beacon started using :meth:`keepalive`.

        .. seealso::

            * :meth:`keepalive`
        """
        if self._keepalive_timer is not None:
            self._keepalive_timer.cancel()
            self._keepalive_timer = None

        self._keepalive_interval = None
        return None            

    def keepalive(self, interval=540):
        """
        Starts or restarts a timer which sends each *interval* seconds a beacon
        to the ts3 server to prevent closing the connection due to the max idle
        time.

        :arg interval:
            Time between a beacon is sent to the server. This should be less than
            the maximum allowed idle time. Usually, this value is set to 600s on
            a TS3 server. 

        .. seealso::

            * :meth:`cancel_keepalive`
        """
        # Sending a beacon now, will create a new timer
        # or restart the timer with the new intervall.
        self._keepalive_interval = interval
        self.__send_keepalive_beacon()
        return None

    # Receiving
    # -------------------------
    
    #: This signal is emitted, whenever the server reported an event. Note,
    #: that you must use ``servernotifyregister`` to subscribe to ts3 server
    #: events.
    #: 
    #: You can easily subscribe to the signal:
    #: 
    #: >>> @TS3Connection.on_event.connect
    #: ... def my_handler(sender, event):
    #: ...     print("received event:")
    #: ...     print("  sender:", sender)
    #: ...     print("  event: ", event)
    #: ...     return None
    #: 
    #: If you want to use an handler only for one connection, you can use
    #: ``connect_via`` to filter the signals:
    #: 
    #: >>> ts3conn = TS3Connection()
    #: >>> @TS3Connection.on_event.connect_via(ts3conn)
    #: ... def my_handler(sender, event):
    #: ...     pass
    #: 
    #: The first argument is the ``TS3Connection`` that received the event
    #: and the second argument is the received event packed into a ``TS3Event``.
    #:
    #: Note, that the events are dispatched in a dedicated **thread**. 
    on_event = blinker.Signal()
    
    def wait_for_resp(self, query_id, timeout=None):
        """
        Waits for an response. This method will block untill the response to
        the query has been received, when *timeout* exceeds or when the
        connection is closed.

        :arg query_id:
            The id of the query internally used to identify the corresponding
            response.
        :type query_id:
            int

        :arg timeout:
            Maximum time in seconds waited for the response.
        :type timeout:
            None or int

        :raises TS3ResponseRecvError:
            If the response could not be received, because the connection has
            been closed or the timeout has been exceeded.            
        :raises TS3QueryError:
            If the *error id* of the query was not 0.               
        """
        if timeout is None:
            end_time = None
        else:
            end_time = time.time() + timeout

        while True:
            # We need to catch this case here, to avoid dead locks, when we
            # are not in threading mode.
            if query_id in self._responses:
                break           
            if not self.is_connected():
                break
            if timeout is not None and time.time() < end_time:
                break
            
            # Wait for a new response and try to find the
            # response corresponding to the query.
            with self._new_response_event:
                self._new_response_event.wait(timeout=0.1)

        resp = self._responses.get(query_id)
        if resp is None or not self.is_connected():
            raise TS3ResponseRecvError()
        if resp.error["id"] != "0":
            raise TS3QueryError(resp)
        return resp
    
    def stop_recv(self):
        """
        If :meth:`recv` has been called from another thread, it will be
        told to stop.
        This method blocks, until :meth:`recv` has terminated.
        """
        if self._is_listening:
            self._stop_event.clear()
            self._waiting_for_stop = True
            self.__event_dispatcher.stop()
            self._stop_event.wait()
        return None

    def recv_in_thread(self):
        """
        Calls :meth:`recv` in a thread. This is useful,
        if you used ``servernotifyregister`` and you expect to receive events.
        """
        thread = threading.Thread(target=self.recv, args=(True,))
        thread.start()
        return None

    def recv(self, recv_forever=False, poll_intervall=0.5):
        """
        Blocks untill all unfetched responses have been received or
        forever, if *recv_forever* is true.

        .. deprecated:: 0.6.0
            The *recv_forever* argument will be removed in future versions.
            Use :meth:`recv_in_thread` instead.
            
        :arg recv_forever:
            If true, this method waits forever for a response and you have to
            call :meth:`stop_recv` from another thread, to stop it.
        :type recv_forever:
            bool           

        :arg poll_intervall:
            Seconds between checks for the stop request.
        :type poll_intervall:
            float

        :raises RuntimeError:
            When the client is already listening.
        """           
        if self._is_listening:
            raise RuntimeError("Already receiving data!")
        
        self._is_listening = True
        try:
            lines = list()
            # Stop, when
            # * the client is disconnected.
            # * the stop flag is set.
            # * we don't recv forever and we don't wait for responses.
            while self.is_connected() \
                  and (not self._waiting_for_stop) \
                  and (self.remaining_responses() or recv_forever):

                # Read one line
                # 1.) An event (Note, that an event has no trailing error line)
                # 2.) Query response
                # 3.) The error line of the query response.                
                data = self._telnet_conn.read_until(
                    b"\n\r", timeout=poll_intervall)
                if not data:
                    continue

                # We received an event.
                if data.startswith(b"notify"):
                    event = TS3Event([data])

                    # We start the event dispatcher as late as possible to
                    # avoid unnecessairy threads.
                    self.__event_dispatcher.start()
                    self.__event_dispatcher.send(
                        self.on_event, self, event=event
                        )
                    
                # We received the end of a query response.
                elif data.startswith(b"error"):
                    lines.append(data)
                    
                    resp = TS3QueryResponse(lines)
                    lines = list()
                    
                    self._query_id += 1
                    self._responses[self._query_id] = resp

                    with self._new_response_event:
                        self._new_response_event.notify_all()
                        
                # There's no keyword, so it must be a part of a query response.
                else:
                    lines.append(data)
                    
        # Catch socket and telnet errors
        except (OSError, EOFError) as err:
            # We need to set this flag here, to avoid dead locks while closing.
            self._is_listening = False
            self.close()
            raise
        finally:
            self._stop_event.set()
            self._waiting_for_stop = False
            self._is_listening = False
        return None
    
    # Sending
    # -------------------------

    def send(self, command, common_parameters=None, unique_parameters=None,
             options=None, timeout=None):
        """
        The general structure of a query command is::

            <command> <options> <common parameters> <unique parameters>|<unique parameters>|...

        Examples are here worth a thousand words:

        >>> # clientaddperm cldbid=16 permid=17276 permvalue=50 permskip=1|permid=21415 permvalue=20 permskip=0
        >>> ts3conn.send(
        ...     command = "clientaddperm",
        ...     common_paramters = {"cldbid": 16},
        ...     parameterlist = [
        ...         {"permid": 17276, "permvalue": 50, "permskip": 1},
        ...         {"permid": 21415, "permvalue": 20, "permskip": 0}
        ...         ]
        ...     )
        >>> # clientlist -uid -away
        >>> ts3conn.send(
        ...     command = "clientlist",
        ...     options = ["uid", "away"]
        ...     )

        .. seealso::
            :meth:`recv`, :meth:`wait_for_resp`
        """
        # Escape the command and build the final query command string.
        if not isinstance(command, str):
            raise TypeError("*command* has to be a string.")
        
        command = command
        common_parameters = TS3Escape.escape_parameters(common_parameters)
        unique_parameters = TS3Escape.escape_parameterlist(unique_parameters)
        options = TS3Escape.escape_options(options)
        
        query_command = command\
                        + " " + common_parameters\
                        + " " +  unique_parameters\
                        + " " + options \
                        + "\n\r"
        query_command = query_command.encode()

        # Send the command.
        with self._send_lock:
            self._telnet_conn.write(query_command)
            # To identify the response when we receive it.
            self._query_counter += 1
            query_id = self._query_counter

        # Make sure, that we receive the command if we are not in
        # threading mode.
        try:
            self.recv()
        except RuntimeError:
            pass                
        return self.wait_for_resp(query_id, timeout)
    

class TS3Connection(TS3BaseConnection, TS3Commands):
    """
    TS3 server query client.

    This class provides the command wrapper capabilities
    :class:`~commands.TS3Commands` and the ability to handle a
    connection to a TeamSpeak 3 server of :class:`TS3BaseConnection`.

    >>> with TS3Connection("localhost") as tsconn:
    ...     # From the TS3Commands class:
    ...     ts3conn.login("serveradmin", "FooBar")
    ...     ts3conn.clientkick(1)
    """

    def _return_proxy(self, command, common_parameters, unique_parameters,
                      options):
        """
        Executes the command created with a method of TS3Commands directly.
        """
        return TS3BaseConnection.send(
            self, command, common_parameters, unique_parameters, options)

    def quit(self):
        """
        Calls :meth:`TS3BaseConnection.close()`, to make sure we leave the
        TS3BaseConnection (pending queries, ...) in a consitent state and that
        running threads are terminated properly.
        """
        self.close()
        return None
