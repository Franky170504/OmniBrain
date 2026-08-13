class TableRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, table_id):
        raise NotImplementedError

    def create(self, table):
        raise NotImplementedError
