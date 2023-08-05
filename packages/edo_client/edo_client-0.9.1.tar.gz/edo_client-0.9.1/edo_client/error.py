#coding:utf8

class ApiError(Exception):
    def __init__(self, status, code, message):
        self.status = status
        self.code = code
        self.message = message

    def __str__(self):
        return "status: %s, code: %s, \nerror message: %s" % (self.status, self.code, self.message)
