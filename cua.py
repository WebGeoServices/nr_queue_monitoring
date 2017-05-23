import redis


class Config(object):
    def __init__(self, host, port, database, prefix):
        self.HOST = host
        self.PORT = port
        self.DATABASE = database
        self.PREFIX = prefix


class Queue(object):
    def __init__(self, config):
        config = config
        self._redis = redis.StrictRedis(host=config.HOST, port=config.PORT,
                                        db=config.DATABASE)

        self.prefix = config.PREFIX
        self.todo_name = self.prefix + ':todo'
        self.doing_name = self.prefix + ':doing'
        self.failed_name = self.prefix + ':failed'

    def get_todo_count(self):
        return self._redis.llen(self.todo_name)

    def get_doing_count(self):
        return self._redis.llen(self.doing_name)

    def get_failed_count(self):
        return self._redis.llen(self.failed_name)