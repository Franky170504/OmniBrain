class DataSourceRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, datasource_id):
        raise NotImplementedError

    def create(self, datasource):
        raise NotImplementedError
