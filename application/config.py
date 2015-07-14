
class Config(object):
    SECRET_KEY = 'very-secret-key'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/promtal"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}