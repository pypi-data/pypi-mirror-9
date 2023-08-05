
class NotFound(object):
    def get(self, k, d=None):
        return None


not_found = NotFound()