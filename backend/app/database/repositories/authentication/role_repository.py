class RoleRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, role_id):
        raise NotImplementedError

    def create(self, role):
        raise NotImplementedError
