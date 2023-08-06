class lookahead(object):
    """An iterator wrapper that allows peeking at the next value without consuming it."""
    def __init__(self, it):
        self.it = iter(it)
        try:
            self.peek = self.it.next()
        except StopIteration:
            pass
    def __iter__(self):
        return self
    def next(self):
        try:
            return self.peek
        except:
            raise StopIteration
        finally:
            try:
                self.peek = self.it.next()
            except StopIteration:
                if hasattr(self, 'peek'):
                    del self.peek
