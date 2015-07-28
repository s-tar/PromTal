class User:
    def is_guest(self):
        return self.id is None

    def is_authorized(self):
        return not self.is_guest()
