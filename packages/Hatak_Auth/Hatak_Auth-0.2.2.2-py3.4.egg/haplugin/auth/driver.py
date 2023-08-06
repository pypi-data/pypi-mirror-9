from haplugin.sql.driver import SqlDriver


class AuthDriver(SqlDriver):
    name = 'Auth'

    def __init__(self, user_cls):
        super().__init__()
        self.model = user_cls

    def get_by_email(self, email):
        return self.query(self.model).filter_by(email=email).first()
