import re
import logging

from lymph.core.interfaces import Component
from lymph.core import trace


logger = logging.getLogger(__name__)


class Event(object):
    def __init__(self, evt_type, body, source=None, headers=None, event_id=None):
        self.event_id = event_id
        self.evt_type = evt_type
        self.body = body
        self.source = source
        self.headers = headers or {}

    def __getitem__(self, key):
        return self.body[key]

    def __iter__(self):
        return iter(self.body)

    def __repr__(self):
        return '<Event type=%r body=%r>' % (self.evt_type, self.body)

    def __str__(self):
        return '{type=%s id=%s}' % (self.evt_type, self.event_id)

    @classmethod
    def deserialize(cls, data):
        return cls(data.get('type'), data.get('body', {}), source=data.get('source'), headers=data.get('headers'))

    def serialize(self):
        return {
            'type': self.evt_type,
            'headers': self.headers,
            'body': self.body,
            'source': self.source,
        }


class EventHandler(Component):
    def __init__(self, interface, func, event_types, sequential=False, queue_name=None, active=True):
        self.func = func
        self.event_types = event_types
        self.sequential = sequential
        self.active = active
        self.interface = interface
        self._queue_name = queue_name or func.__name__

    @property
    def queue_name(self):
        return '%s-%s' % (self.interface.name, self._queue_name)

    @queue_name.setter
    def queue_name(self, value):
        self._queue_name = value

    def on_start(self):
        self.interface.container.subscribe(self, consume=self.active)

    def __call__(self, event, *args, **kwargs):
        trace.set_id(event.headers.get('trace_id'))
        logger.debug('<E %s', event)
        return self.func(self.interface, event, *args, **kwargs)


class EventDispatcher(object):
    wildcards = {
        '#': r'[\w.]*(?=\.|$)',
        '*': r'\w+',
    }

    def __init__(self, patterns=()):
        self.patterns = []
        self.update(patterns)

    def compile(self, key):
        words = (self.wildcards.get(word, re.escape(word)) for word in key.split('.'))
        return re.compile('^%s$' % r'\.'.join(words))

    def register(self, pattern, handler):
        self.patterns.append((
            self.compile(pattern),
            pattern,
            handler,
        ))

    def __iter__(self):
        for regex, pattern, handler in self.patterns:
            yield pattern, handler

    def update(self, other):
        for pattern, handler in other:
            self.register(pattern, handler)

    def dispatch(self, evt_type):
        for regex, pattern, handler in self.patterns:
            if regex.match(evt_type):
                yield pattern, handler

    def __call__(self, event):
        handlers = set()
        for pattern, handler in self.dispatch(event.evt_type):
            if handler not in handlers:
                handlers.add(handler)
                handler(event)
        return bool(handlers)

