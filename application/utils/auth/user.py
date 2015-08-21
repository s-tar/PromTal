class User():
    def __init__(self):
        self.id = None
        self.roles = None
        self.is_admin = None

    def is_guest(self):
        return not hasattr(self, 'id') or self.id is None

    def is_authorized(self):
        return not self.is_guest()

    def can_administrate(self):
        return self.is_admin or ('moderator' in [r.name for r in self.roles])
