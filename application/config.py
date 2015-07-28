
class Config:

    CSRF_ENABLED = True
    SECRET_KEY = 'very-secret-key'

    POSTGRESQL_HOST = 'localhost'
    POSTGRESQL_PORT = 5432
    POSTGRESQL_USERNAME = 'postgres'
    POSTGRESQL_PASSWORD = 'postgres'
    POSTGRESQL_DB_NAME = 'promtal'

    # SQLALCHEMY_ECHO=True
    SQLALCHEMY_DATABASE_URI = "postgresql://{0}:{1}@{2}:{3}/{4}".format(POSTGRESQL_USERNAME,
                                                                        POSTGRESQL_PASSWORD,
                                                                        POSTGRESQL_HOST,
                                                                        POSTGRESQL_PORT,
                                                                        POSTGRESQL_DB_NAME)
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_USERNAME = ''
    REDIS_PASSWORD = ''
    REDIS_DB_NAME = '0'
    REDIS_URL = "redis://{0}:{1}@{2}:{3}/{4}".format(REDIS_USERNAME,
                                                     REDIS_PASSWORD,
                                                     REDIS_HOST,
                                                     REDIS_PORT,
                                                     REDIS_DB_NAME)
    LDAP_SCHEMA = 'ldap'
    LDAP_HOST = 'cirno.uaprom'
    LDAP_PORT = 389
    LDAP_USERNAME = 'cn=admin,dc=uaprom,dc=net'
    LDAP_PASSWORD = '3q1ID69g0fJVHoJp'
    LDAP_BASE_DN = 'dc=uaprom,dc=net'

    LDAP_USER_BASE_DN = 'ou=People,' + LDAP_BASE_DN
    LDAP_USER_OBJECT_FILTER = '(cn=%s)'
    LDAP_USER_PASSWORD_FIELD = 'userPassword'
    LDAP_USER_FIELDS = ['cn', 'displayName', 'mail', 'mobile', 'telephoneNumber']

    LDAP_GROUP_BASE_DN = 'ou=Group,' + LDAP_BASE_DN
    LDAP_GROUP_OBJECT_FILTER = '(cn=%s)'
    LDAP_GROUP_MEMBER_FIELD = 'member'
    LDAP_GROUP_FIELDS = ['cn']

    session = {
        'session.type': 'file',
        'session.cookie_expires': True,
        'session.data_dir': './tmp/session',
        'session.auto': True,
    }

    ADMIN_USERS_PER_PAGE = 20
    ADMIN_NEWS_PER_PAGE = 20

    files = {
        'path': './application/files'
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