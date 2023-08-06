

class HttpException(Exception):

    def __init__(self, status, message, content):
        self.status = status
        self.message = message
        self.content = content

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "HttpException(%s): %s%s" % (
            self.status, self.content,
            "\n%s" % self.message if self.message else "")


class ConnectionException(Exception):

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "ConnectionException: %s" % self.content


class JsonException(Exception):

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "JsonException: %s" % self.content


class ApiException(Exception):

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "ApiException: %s" % self.content
