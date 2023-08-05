__author__ = 'Reza Safaeiyan'


class ReConfig():
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 6379
        self.db = 0
        self.password = None

        self.secret_key = "YourSecretKey"
        self.expire_time = 7200

    def set(self, **kwargs):
        self.host = kwargs['host'] if 'host' in kwargs else '127.0.0.1'
        self.port = kwargs['port'] if 'port' in kwargs else 6379
        self.db = kwargs['db'] if 'db' in kwargs else 0
        self.password = kwargs['password'] if 'password' in kwargs else None

        self.secret_key = kwargs['secret_key'] if 'secret_key' in kwargs else "YourSecretKey"
        self.expire_time = kwargs['expire_time'] if 'expire_time' in kwargs else 7200


config = ReConfig()