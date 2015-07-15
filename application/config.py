
class Config:
    SECRET_KEY = 'very-secret-key'

    POSTGRESQL_HOST = 'localhost'
    POSTGRESQL_PORT = 5432
    POSTGRESQL_USERNAME = 'postgres'
    POSTGRESQL_PASSWORD = 'postgres'
    POSTGRESQL_DB_NAME = 'promtal'

    SQLALCHEMY_DATABASE_URI = "postgresql://{0}:{1}@{2}:{3}/{4}".format(POSTGRESQL_USERNAME,
                                                                        POSTGRESQL_PASSWORD,
                                                                        POSTGRESQL_HOST,
                                                                        POSTGRESQL_PORT,
                                                                        POSTGRESQL_DB_NAME)

    LDAP_SCHEMA = 'ldap'
    LDAP_HOST = ''
    LDAP_PORT = 389
    LDAP_USERNAME = ''
    LDAP_PASSWORD = ''
    LDAP_BASE_DN = 'ou=,dc=,dc='
    LDAP_USER_OBJECT_DN = 'cn'
    LDAP_USER_OBJECT_FILTER = '(cn=*)'
    LDAP_USER_FIELD = ['cn', 'displayName', 'mail', 'mobile', 'telephoneNumber']

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