import requests

from flask import current_app


class SkySMS(object):
    SUBMIT_URL = 'http://sms.skysms.net/api/submit_sm'

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        app.config.setdefault('SKYSMS_USERNAME', None)
        app.config.setdefault('SKYSMS_PASSWORD', None)
        app.config.setdefault('SKYSMS_PASSWORD_MESSAGE', 'Login:%(login)s\nPassword:%(password)s')
        app.config.setdefault('SKYSMS_MSGCHRSET', None)
        app.config.setdefault('SKYSMS_MSGENCODING', None)

        for option in ['USERNAME', 'PASSWORD']:
            if app.config['SKYSMS_{0}'.format(option)] is None:
                raise ValueError('SKYSMS_{0} cannot be None!'.format(option))

    def send_message(self, phone_number, message):
        response = requests.get(self.SUBMIT_URL, params={'login': current_app.config['SKYSMS_USERNAME'],
                                                         'passwd': current_app.config['SKYSMS_PASSWORD'],
                                                         'destaddr': phone_number,
                                                         'msgchrset': current_app.config['SKYSMS_MSGCHRSET'],
                                                         'msgtext': message.encode(
                                                            current_app.config['SKYSMS_MSGENCODING']
                                                         )})
        return response

    def send_password(self, phone_number, login, password):
        message = current_app('SKYSMS_PASSWORD_MESSAGE') % {'login': login, 'password': password}
        return self.send_message(phone_number, message)
