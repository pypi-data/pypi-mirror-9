'''
Tyuio is a Simple Event Dispatcher api

@author: Moises P. Sena <moisespsena@gmail.com>
'''


class EventType(object):
    '''
    The Event Type
    '''

    def __init__(self, evcls, evtype):
        self.evcls = evcls
        self.evtype = evtype

    def __hash__(self):
        return hash((self.evcls, self.evtype))

    def __repr__(self):
        return "<EventType(%r, %r)>" % (self.evcls, self.evtype)

    def __str__(self):
        return "%r.%s" % (self.evcls, self.evtype)

    def __eq__(self, other):
        if isinstance(other, EventType):
            if other.evcls == self.evcls:
                if other.evtype == self.evtype:
                    return True
        return False


class Event(object):
    """
    Generic Event object to use with EventDispatcher.

    Example:

    >>> dispatcher = EventDispatcher()
    >>> def callback(e, *args, **kwargs):
    ...     print(e.type)
    >>> dispatcher.add_event_listener("my_type", callback)
    <EventDispatcher()>
    >>> dispatcher.dispatch(Event("my_type"))
    my_type
    <Event('my_type')>
    """

    def __init__(self, event_type):
        """
        The constructor accepts an event type as string and a custom data
        """
        self.type = event_type
        self.targets = []
        self.called_listeners = None
        self._tmp_target = None

    def __enter__(self):
        """
        Enter in new dispatch context
        Enter in new dispatch context. Append current target in
        ``self.targets`` list.
        :return: The target object

        Example:

        >>> class D1(EventDispatcher): pass
        >>> class D2(EventDispatcher): pass
        >>> d1 = D1()
        >>> d2 = D2()
        >>> event = Event("my_type")
        >>> with event(d1):
        ...     print(event.source_target)
        ...     print(event.current_target)
        ...     print(event.targets)
        ...
        ...     with event(d2):
        ...         print(event.source_target)
        ...         print(event.current_target)
        ...         print(event.targets)
        <D1()>
        <D1()>
        [<D1()>]
        <D1()>
        <D2()>
        [<D1()>, <D2()>]
        """
        assert self._tmp_target
        self.targets.append(self._tmp_target)
        self._tmp_target = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Return last inserted target object in ``self.targets`` list.
        :return: The target object
        """
        assert not self._tmp_target
        self.targets.pop()

    def __call__(self, target):
        """
        Add ``target`` for use it in ``with`` expression.
        :param target: The new event target
        :return: self event object
        """
        assert not self._tmp_target
        self._tmp_target = target
        return self

    @property
    def current_target(self):
        """
        Return last target object in ``self.targets`` list.
        :return: The target object
        """
        return self.targets[-1]

    @property
    def source_target(self):
        """
        Return first target object in ``self.targets`` list.
        :return: The target object
        """
        return self.targets[0]

    def __repr__(self):
        return "<Event(%r)>" % (self.type)


class Listener(object):
    """Listener interface"""

    def __call__(self, event, *args, **kwargs):
        """Listener invoker"""
        raise NotImplementedError()


def is_iter(obj):
    '''
    Check if obj contains '__iter__' attribute
    :param obj: the object of check
    :return: ``True`` if contains, other else, ``False``
    '''
    return hasattr(obj, '__iter__')


class EventDispatcher(object):
    """
    Generic event dispatcher which listen and dispatch events

    Examples:

    >>> d = EventDispatcher()

    or

    >>> class Target(object):
    ...     def __repr__(self):
    ...         return '<%s object>' % self.__class__.__name__
    >>> d = EventDispatcher(Target())
    >>> d.target
    <Target object>

    Add listeners:

    >>> def callback(e, *args, **kwargs):
    ...     pass
    >>> d.add_event_listener('my_event', callback)
    <EventDispatcher(target=<Target object>)>
    >>> d.add_event_listeners('my_event', callback, callback)
    <EventDispatcher(target=<Target object>)>
    >>> d.add_events_listeners(('my_event', [callback, callback]))
    <EventDispatcher(target=<Target object>)>
    >>> d.add_events_listeners(('my_event', [callback, callback]), \
    ('another_event', [callback, callback]))
    <EventDispatcher(target=<Target object>)>
    """

    def __init__(self, target=None):
        """Kwargs:
        - target: The event target. Default is ``None``
        """
        self._event_listeners = dict()
        self._target = target

    @property
    def target(self):
        return self._target or self

    def __del__(self):
        """
        Remove all listener references at destruction time
        """
        self._event_listeners = None

    def has_listener(self, event_type, listener):
        """
        Check if dispatch contains the ``listener`` of ``event_type`` event type.
        :param event_type: The event type
        :param listener: The listener callback
        :return: ``True`` if contains, other else, ``False``
        """
        # Check for event type and for the listener
        if event_type in self._event_listeners.keys():
            return listener in self._event_listeners[event_type]
        else:
            return False

    def _invoke_listener(self, listener, event, *args, **kwargs):
        return listener(event, *args, **kwargs)

    def dispatch(self, event, *args, **kwargs):
        """
        Dispatch all listeners of ``event.type``

        :param event: The event object
        :param args: Args to pass at listener function
        :param kwargs: Keyword args to pass at listener function
        :return: the ``event`` object

        >>> dispatcher = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     print(e.type)
        >>> dispatcher.add_event_listener("my_type", callback)
        <EventDispatcher()>
        >>> dispatcher.dispatch(Event("my_type"))
        my_type
        <Event('my_type')>
        """
        event.called_listeners = []

        # Dispatch the event to all the associated listeners 
        if event.type in self._event_listeners:
            listeners = self._event_listeners[event.type]
            with event(self.target):
                for listener in listeners:
                    event.called_listeners.append(listener)
                    # call listener and stop if returns False
                    if self._invoke_listener(listener, event, *args,
                                             **kwargs) is False:
                        break
        return event

    def add_event_listener(self, event_type, listener):
        """
        Add one listener at event type

        :param event_type: The event type
        :param listener: The listener
        :return: the ``self`` object

        Example:

        >>> d = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     pass
        >>> d.add_event_listener('my_event', callback)
        <EventDispatcher()>
        """
        # Add listener to the event type
        if not self.has_listener(event_type, listener):
            listeners = self._event_listeners.get(event_type, [])
            listeners.append(listener)
            self._event_listeners[event_type] = listeners
        return self

    on = add_event_listener

    def add_event_listeners(self, event_type, *listeners):
        """
        Add one or more listeners at event type

        :param event_type: The event type
        :param listeners: The listener list
        :return: the ``self`` object

        Example:

        >>> d = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     pass
        >>> d.add_events_listeners('my_event', [callback, callback])
        <EventDispatcher()>
        """
        if len(listeners) == 1 and is_iter(listeners[0]):
            listeners = listeners[0]

        for _ in listeners:
            self.add_event_listener(event_type, _)
        return self

    def add_events_listeners(self, *types_with_listeners):
        """
        Add multiples listeners on varios events types.

        :param types_with_listeners: tuples of (event_type, listeners)
        :return: the ``self`` object

        Example:

        >>> d = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     pass
        >>> d.add_events_listeners(('my_event', [callback, callback]), ('another_event', [callback, callback]))
        <EventDispatcher()>
        """
        if len(types_with_listeners) == 1 and is_iter(types_with_listeners[0]):
            types_with_listeners = types_with_listeners[0]

        for _ in types_with_listeners:
            self.add_event_listeners(*_)
        return self

    def remove_event_listener(self, event_type, listener):
        """
        Remove one listener at event type

        :param event_type: The event type
        :param listener: The listener
        :return: the ``self`` object

        Example:

        >>> d = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     pass
        >>> d.remove_event_listener('my_event', callback)
        <EventDispatcher()>
        """
        # Remove the listener from the event type
        if self.has_listener(event_type, listener):
            listeners = self._event_listeners[event_type]

            if len(listeners) == 1:
                # Only this listener remains so remove the key
                del self._event_listeners[event_type]

            else:
                # Update listeners chain
                listeners.remove(listener)

                self._event_listeners[event_type] = listeners
        return self

    def remove_event_listeners(self, event_type, *listeners):
        """
        Remove one or more listeners at event type

        :param event_type: The event type
        :param listeners: The listener list
        :return: the ``self`` object

        Example:

        >>> d = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     pass
        >>> d.remove_events_listeners('my_event', [callback, callback])
        <EventDispatcher()>
        """
        if len(listeners) == 1 and is_iter(listeners[0]):
            listeners = listeners[0]

        for _ in listeners:
            self.remove_event_listener(event_type, _)
        return self

    def remove_events_listeners(self, *types_with_listeners):
        """
        Removes multiples listeners on varios events types.

        :param types_with_listeners: tuples of (event_type, listeners)
        :return: the ``self`` object

        Example:

        >>> d = EventDispatcher()
        >>> def callback(e, *args, **kwargs):
        ...     pass
        >>> d.remove_events_listeners(('my_event', [callback, callback]),('another_event', [callback, callback]))
        <EventDispatcher()>
        """
        if len(types_with_listeners) == 1 and \
                is_iter(types_with_listeners[0]):
            types_with_listeners = types_with_listeners[0]

        for _ in types_with_listeners:
            self.remove_event_listeners(*_)
        return self

    def remove_all_listeners(self):
        """
        Remove all events listeners
        :return: the ``self`` object
        """
        self._event_listeners = {}
        return self

    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__,
                             self._target and \
                             ('target=%r' % self._target) or '')