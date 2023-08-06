
class Notification(object):
    def __init__(self, source, title, data=None):
        self._source=source
        self._title=title
        self._data=data

    @property
    def source(self):
        return self._source
    
    @property
    def title(self):
        return self._title

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        try:
            return self._data[key]
        except:
            pass

    def validate(self):
        return True

    def __repr__(self):
        return '%s:%s' % (self.source, self.title)


class NotificationCallToPager(Notification):
    def __init__(self, source, data):
        super(NotificationCallToPager, self).__init__(source, 'calltopager', data)

    @property
    def callAddress(self):
        return self['1']

    @property
    def message(self):
        return self['2']

    def validate(self):
        if self.callAddress and self.message:
            return True

    def __repr__(self):
        return '%s:%s(%s,%s)' % (self.source, self.title, self.callAddress, self.message)


class NotificationLinkTimeout(Notification):
    def __init__(self, source):
        super(NotificationLinkTimeout, self).__init__(source, 'linktimeout')


if __name__=='__main__':
    pass