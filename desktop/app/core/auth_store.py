# desktop/app/core/auth_store.py
class AuthStore:

    def __init__(self):
        self.access = None
        self.refresh = None

    def set_tokens(self, access: str, refresh: str):
        self.access = access
        self.refresh = refresh

    def clear(self):
        self.access = None
        self.refresh = None

    def is_authenticated(self):
        return self.access is not None