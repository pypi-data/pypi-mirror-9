from weppy._compat import hashlib_md5


def make_md5(value):
    return hashlib_md5(value.encode('utf8')).hexdigest()[:8]


class HamlCache(object):
    data = {}
    hashes = {}

    def get(self, filename, source):
        hashed = make_md5(source)
        if self.hashes.get(filename) != hashed:
            return None
        return self.data.get(filename)

    def set(self, filename, source, compiled):
        self.data[filename] = compiled
        self.hashes[filename] = make_md5(source)
