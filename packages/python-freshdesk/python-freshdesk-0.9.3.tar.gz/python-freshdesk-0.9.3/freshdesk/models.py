from dateutil.parser import parser as datetime_parser

class FreshdeskModel(object):
    _keys = set()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(Ticket, k):
                k = '_' + k
            setattr(self, k, v)
            self._keys.add(k)
        self.created_at = self._to_timestamp(self.created_at)
        self.updated_at = self._to_timestamp(self.updated_at)

    def _to_timestamp(self, timestamp_str):
        """Converts a timestamp string as returned by the API to
        a native datetime object and return it."""
        return datetime_parser(timestamp_str)

class Ticket(FreshdeskModel):
    def __str__(self):
        return self.subject

    def __repr__(self):
        return '<Ticket \'{}\'>'.format(self.subject)

    @property
    def comments(self):
        return [Comment(ticket=self, **c['note']) for c in self.notes]

    @property
    def priority(self):
        _p = {1: 'low', 2: 'medium', 3: 'high', 4: 'urgent'}
        return _p[self._priority]

    @property
    def status(self):
        _s = {2: 'open', 3: 'pending', 4: 'resolved', 5: 'closed'}
        try:
            return _s[self._status]
        except KeyError:
            return 'status_{}'.format(self._status)

    @property
    def source(self):
        _s = {1: 'email', 2: 'portal', 3: 'phone', 4: 'forum', 5: 'twitter', 6: 'facebook', 7: 'chat'}
        return _s[self._source]

class Comment(FreshdeskModel):
    def __str__(self):
        return self.body

    def __repr__(self):
        return '<Comment for {}>'.format(repr(self.ticket))

class Contact(FreshdeskModel):
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Contact \'{}\'>'.format(self.name)
