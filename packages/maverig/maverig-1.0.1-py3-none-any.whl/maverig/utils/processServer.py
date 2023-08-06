from collections import namedtuple
import multiprocessing

from PySide import QtCore


Call_Pack = namedtuple('Call_Pack', 'func_name args kwargs')  # transfer method format


class Server:
    def __init__(self, interval=40):
        super().__init__()
        self.call_queue = multiprocessing.Queue()

        self.interval = interval
        self._timer = None
        self.func_names = set()

    def register_function(self, func_name):
        """ register a function that can be called via proxy """
        self.func_names.add(func_name)

    def start(self):
        self._timer = QtCore.QTimer()  # QTimer's run method seems to be thread-safe for access on QT-widgets
        self._timer.timeout.connect(self.run)
        self._timer.start(self.interval)

    def run(self):
        """ repeatedly listens to incoming function calls and trigger them """
        while not self.call_queue.empty():
            func_name, args, kwargs = self.call_queue.get()
            func = getattr(self, func_name)
            func(*args, **kwargs)

    def stop(self):
        if self._timer:
            self._timer.stop()


class ProcessServer(Server):
    def __init__(self, interval=40):
        super().__init__(interval)
        self.process_factories = []  # map from process_factory to process
        self.processes = []

    def register_process_factory(self, process_factory):
        self.process_factories.append(process_factory)

    def start(self):
        """ start simulation and run in a simulation process """
        super().start()
        for process_factory in self.process_factories:
            process = process_factory()
            self.processes.append(process)
            process.start()

    def stop(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
        self.processes.clear()
        super().stop()


class MethodProxy:
    def __init__(self, func_name, call_queue):
        self.func_name = func_name
        self.call_queue = call_queue

    def __call__(self, *args, **kwargs):
        self.call_queue.put(Call_Pack(self.func_name, args, kwargs))


class ServerProxy:
    """ subprocess (~client) side access to registered server functions
    Calls can currently only be one-directional. Function return values are ommitted. """

    def __init__(self, server):
        self.call_queue = server.call_queue

        for func_name in server.func_names:
            self.__dict__[func_name] = MethodProxy(func_name, self.call_queue)
