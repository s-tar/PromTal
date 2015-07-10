from application.utils.immutable import imdict

config = imdict({
    'files':{
        'path':'./files'
    },
    'session': {
        'session.type': 'file',
        'session.cookie_expires': True,
        'session.data_dir': './tmp/session',
        'session.auto': True
    },
    'db': {
        'type': 'mysql',
        'host': "localhost",
        'db': 'promtal',
        'port': 3306,
        'username': 'root',
        'password': '',
    }
})