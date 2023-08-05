class AsyncnotiException(Exception):
    def __init__(self, message, code):
        super(Exception, self).__init__(message)
        self.message = message
        self.code = code
