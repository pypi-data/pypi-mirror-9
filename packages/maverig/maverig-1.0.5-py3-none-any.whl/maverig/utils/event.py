class Event:
    """ Simple Event Class - see: http://www.valuedlessons.com/2008/04/events-in-python.html
    usage:

    """

    def __init__(self):
        self.__handlers = set()
        self.demanded = False
        self.demands_count = 0
        self.update_level = 0

    def handle(self, handler):
        self.__handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.__handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def __enter__(self):
        """ begin updating """
        self.update_level += 1

    def __exit__(self, *args):
        """ end updating """
        self.update_level -= 1
        if self.update_level == 0 and self.demanded:
            self.fire()

    """ register a demand fore firing this event """

    def demand(self):
        self.demanded = True
        self.demands_count += 1

    def fire(self, *args, **kwargs):
        """ fires the event with given arguments and return a list of results of each call """
        if self.update_level > 0:
            self.demand()
            return

        results = []
        self.demanded = False
        for handler in self.__handlers.copy():
            if handler in self.__handlers:
                handler_result = handler(*args, **kwargs)
                results.append(handler_result)
        return results

    def get_handler_count(self):
        return len(self.__handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = get_handler_count