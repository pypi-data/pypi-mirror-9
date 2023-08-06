__all__ = ['Event','EventDispatcher']


class Event(object):
    def __init__(self):
        self.handlers = list()

    def handle(self, handler):
        self.handlers.append(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount


class EventDispatcher(object):

    __events__ = []

    def __init__(self):
        for event in self.__events__ :
            self.add_event(event)

    def add_event(self, event_name):
        new_event = Event()
        if hasattr(self, event_name):
            new_event += getattr(self, event_name)
        setattr(self, event_name, new_event)
