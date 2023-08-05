
class NotFound(object):
    def get(self, k, d=None):
        if d == self:
            return d
        return None


not_found = NotFound()