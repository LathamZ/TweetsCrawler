import redis

class DB():
    _db = None
    def __init__(self, host='localhost', port=6379, db=1):
        self._db = redis.StrictRedis(host=host, port=port, db=db)

    def set(self, key, value):
        self._db.set(key, value)

    def get(self, key):
        return self._db.get(key)

    def scan(self, match=None, count=None):
        res = []
        for key in self._db.scan_iter(match, count):
            res.append((key, self.get(key)))
        return res

    def keys(self, pattern="*"):
        return self._db.keys(pattern)

    def count(self, pattern="*"):
        keys = self.keys(pattern)
        if keys is not None:
            return len(keys)
        else:
            return 0

    def clean(self):
        self._db.flushdb()

if __name__ == "__main__":
    db = DB()
    db.set('a', 'test')
    db.set('a2', 'test2')
    db.set('b', "testb")
    print(db.scan(match='a*'))
    print("=======")
    # db.clean()
    print(db.scan(match='a*'))
    print("=======")

