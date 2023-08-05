class Subject(object):
    def __init__(self):
        self.observers = []

    def notify(self, *args, **kwargs):
        """Notify our observers about an event"""
        for observer in self.observers:
            observer.notify(*args, **kwargs)

    def register_observer(self, observer):
        """Keep track of our observer"""
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        """Remove a single observer"""
        if observer in self.observers:
            self.observers.remove(observer)

    def remove_observers(self):
        """Remove all observers"""
        self.observers = []

class ObserverBase(object):
    """Base class for any observers of `Subject`"""
    def notify(self, *args, **kwargs):
        """Subject is updating all observers that an event has occured"""
        raise NotImplementedError()
