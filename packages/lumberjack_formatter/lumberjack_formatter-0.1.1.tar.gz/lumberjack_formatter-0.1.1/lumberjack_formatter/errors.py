class FormatterInitializationException(Exception):
    pass

class IllegalInputException(Exception):
    def __init__(self, key=None, *args, **kwargs):
        self.key = key
        super(IllegalInputException, self).__init__(*args, **kwargs)

# vim: set ts=4 sw=4 expandtab:
