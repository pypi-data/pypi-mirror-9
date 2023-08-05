class BadValue(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class ValueNotPresent(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
