class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        raise NotImplementedError

    def create(self, user):
        raise NotImplementedError
