
class Config:
    SECRET_KEY = 'very-secret-key'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/promtal"

    session = {
        'session.type': 'file',
        'session.cookie_expires': True,
        'session.data_dir': './tmp/session',
        'session.auto': True,
    }

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}