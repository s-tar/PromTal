class User():
    def __init__(self):
        self.id = None

    def is_guest(self):
        return not hasattr(self, 'id') or self.id is None

    def is_authorized(self):
        return not self.is_guest()
