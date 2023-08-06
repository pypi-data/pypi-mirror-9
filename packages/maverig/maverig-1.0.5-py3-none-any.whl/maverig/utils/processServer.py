from collections import namedtuple
#import multiprocessing
import zmq

from PySide import QtCore


Call_Pack = namedtuple('Call_Pack', 'func_name args kwargs')
"""Transfer method format for calling functions via :class:`ServerProxy`."""


class Server:
    """A server managing incoming function calls via zero-mq socket."""

    def __init__(self, interval=40):
        super().__init__()
        self.port = "5556"
        self.socket = None

        self.interval = interval
        self._timer = None
        self.func_names = set()

    def register_function(self, func_name):
        """Register a server function that can be called via proxy."""
        self.func_names.add(func_name)

    def start(self):
        """Start listening to incoming function calls and activate the socket."""
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.setsockopt(zmq.RCVTIMEO, 0)  # Timeout immediately if no function calls enqueued
        self.socket.bind("tcp://*:%s" % self.port)

        self._timer = QtCore.QTimer()  # QTimer's run method seems to be thread-safe for access on QT-widgets
        self._timer.timeout.connect(self.run)
        self._timer.start(self.interval)

    def run(self):
        """Repeatedly listens to incoming function calls as :class:`Call_Pack` and trigger them."""
        try:
            while self.socket:
                # non-blocking function call receive: assure NOBLOCK in case RCVTIMEO is not supported
                func_name, args, kwargs = self.socket.recv_pyobj(zmq.NOBLOCK)
                func = getattr(self, func_name)
                func(*args, **kwargs)
        except zmq.ZMQError:
            pass  # no more function calls to receive.
            # look for function calls on next run call after self.interval milliseconds

    def stop(self):
        """Stop listening to incoming function calls and close socket."""
        if self._timer:
            self._timer.stop()
        if self.socket:
            self.run()  # retrieve pending function calls one last time in case LINGER is not supported
            self.socket.close()
            self.socket = None


class ProcessServer(Server):
    """A server managing subprocesses and their incoming function calls."""

    def __init__(self, interval=40):
        super().__init__(interval)
        self.process_factories = []  # map from process_factory to process
        self.processes = []

    def register_process_factory(self, process_factory):
        """Register a factory method to create a subprocess."""
        self.process_factories.append(process_factory)

    def start(self):
        """Start subprocesses and constantly listen to incoming function calls."""
        super().start()
        for process_factory in self.process_factories:
            process = process_factory()
            self.processes.append(process)
            process.start()

    def stop(self):
        """Stop subprocesses and stop listening to incoming functions."""
        for process in self.processes:
            if process.is_alive():
                process.terminate()
        self.processes.clear()
        super().stop()


class MethodProxy:
    """A callable method proxy that can directly be called on the parent ServerProxy
    with same name and parameters like the Server function."""

    def __init__(self, server_proxy, func_name):
        self.server_proxy = server_proxy
        self.func_name = func_name

    def __call__(self, *args, **kwargs):
        self.server_proxy.socket.send_pyobj(Call_Pack(self.func_name, args, kwargs))


class ServerProxy:
    """Subprocess (~client) side access to registered server functions.
    Calls can currently only be one-directional. Function return values are ommitted."""

    def __init__(self, server):
        self.port = server.port
        self.socket = None
        for func_name in server.func_names:
            self.__dict__[func_name] = MethodProxy(self, func_name)

    def init_socket(self):
        """Activate the socket for sending method calls to *Server* from *Subprocess*.
        **This method must be called from Subprocess!**"""
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://localhost:%s" % self.port)
        self.socket.setsockopt(zmq.LINGER, 0)  # do not keep sending messages after socket close

    def close_socket(self):
        """Close the *Subprocess* socket to *Server*.
        **This method must be called from Subprocess!**"""
        self.socket.close()
