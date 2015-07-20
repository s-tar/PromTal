class User:
    def is_guest(self):
        return self.id is not None

    def is_authorized(self):
        return not self.is_guest()

    def __getattr__(self, item):
        if hasattr(self.__dict__, item):
            return self[item]
        return None