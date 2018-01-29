class Reader:
    __slots__ = ['data', 'cursor']

    def __init__(self):
        self.data = ''
        self.cursor = -1

    def __init__(self, string):
        self.data = string
        self.cursor = 0

    def next(self):
        if self.cursor >= len(self.data):
            return None
        ret = self.data[self.cursor]
        self.cursor += 1
        return ret

    def prev(self, step=1):
        self.cursor = self.cursor - step if self.cursor - step >= 0 else 0

    def has_next(self):
        return self.cursor + 1 <= len(self.data)

    def get_cursor(self):
        return self.cursor

    def get_cursor_data(self):
        if self.cursor >= len(self.data):
            return None
        return self.data[self.cursor]

    def get_prev_data(self, step=1):
        if self.cursor - step >= 0:
            return self.data[self.cursor - step]
        return None

    def get_next_data(self):
        if self.cursor + 1 >= len(self.data):
            return None
        return self.data[self.cursor + 1]


def new_instance(data):
    return Reader(data)
