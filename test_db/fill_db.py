import sys
import configparser
import psycopg2
import ldap3

INI_FILES = ['conf.ini']


def create_conn_to_postgresql(postgresql_config):
    postgresql_server_name = "{0}://{1}:{2}@{3}:{4}/{5}".format('postgresql',
                                                                postgresql_config['POSTGRESQL_USERNAME'],
                                                                postgresql_config['POSTGRESQL_PASSWORD'],
                                                                postgresql_config['POSTGRESQL_HOST'],
                                                                postgresql_config['POSTGRESQL_PORT'],
                                                                postgresql_config['POSTGRESQL_DB_NAME'])

    print("Create connection to {postgresql} ...".format(postgresql=postgresql_server_name))
    postgresql_conn = psycopg2.connect(database=postgresql_config['POSTGRESQL_DB_NAME'],
                                       user=postgresql_config['POSTGRESQL_USERNAME'],
                                       password=postgresql_config['POSTGRESQL_PASSWORD'],
                                       host=postgresql_config['POSTGRESQL_HOST'],
                                       port=postgresql_config['POSTGRESQL_PORT'])
    print("Connection to PostgreSQL server has been created successfully.")

    return postgresql_conn


def create_conn_to_ldap(ldap_config):
    ldap_server_name = "{0}://{1}:{2}".format(ldap_config['LDAP_SCHEMA'],
                                              ldap_config['LDAP_HOST'],
                                              ldap_config['LDAP_PORT'])

    print("Create connection to {ldap} ...".format(ldap=ldap_server_name))
    ldap_conn = ldap3.Connection(server=ldap3.Server(ldap_server_name),
                                 user=ldap_config['LDAP_USERNAME'],
                                 password=ldap_config['LDAP_PASSWORD'],
                                 authentication=ldap3.SIMPLE,
                                 auto_bind=True)
    print("Connection to LDAP server has been created successfully.")

    return ldap_conn


def get_user_details(ldap_conn, ldap_config):
    ldap_conn.search(
        search_base=ldap_config['LDAP_BASE_DN'],
        search_filter=ldap_config['LDAP_USER_OBJECT_FILTER'],
        search_scope=ldap3.SUBTREE,
        attributes=ldap3.ALL_ATTRIBUTES
    )

    for entry in ldap_conn.response:
        yield entry['attributes']


def fill_db():
    print("Start filling ...")

    config = configparser.ConfigParser()
    filenames = config.read(INI_FILES)

    print("Loaded .ini files: {filenames}".format(filenames=", ".join(filenames)))

    postgres_config = config['POSTGRESQL']
    ldap_config = config['LDAP']

    postgresql_conn = create_conn_to_postgresql(postgres_config)
    ldap_conn = create_conn_to_ldap(ldap_config)

    postgresql_cursor = postgresql_conn.cursor()
    for user in get_user_details(ldap_conn, ldap_config):
        postgresql_cursor.execute("INSERT INTO users (login, full_name, mobile_phone, inner_phone, email)"
                                  "VALUES(%s, %s, %s, %s, %s)", (user.get('cn', [''])[0],
                                                                 user.get('displayName', [''])[0],
                                                                 user.get('mobile', [''])[0],
                                                                 user.get('inner_phone', [''])[0],
                                                                 user.get('mail', [''])[0]))
    postgresql_conn.commit()

    ldap_conn.unbind()
    postgresql_conn.close()

if __name__ == '__main__':
    sys.exit(fill_db())
