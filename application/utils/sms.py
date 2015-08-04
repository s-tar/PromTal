import requests
import logging

from flask import current_app

SUBMIT_SM = 'http://sms.skysms.net/api/submit_sm'

RETURNCODE = 'RETURNCODE'
SUCCESS_CODE = '00'
CODEVALUE = {
    '00': 'Сообщение успешно добавлено в очередь',
    '01': 'Недопустимые значения параметров или нет обязательных параметров',
    '02': 'Зарезервировано',
    '03': 'Зарезервировано',
    '04': 'Зарезервировано',
    '05': 'Ошибка аутентификации клиента',
    '06': 'Ошибка настроек клиента',
    '07': 'Ошибка проверки состояния сообщения'
}

class SkySMS(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        app.config.setdefault('SKYSMS_USERNAME', None)
        app.config.setdefault('SKYSMS_PASSWORD', None)
        app.config.setdefault('SKYSMS_LOGFILE', None)
        app.config.setdefault('SKYSMS_PASSWORD_MESSAGE', 'Login:%(login)s\nPassword:%(password)s')
        app.config.setdefault('SKYSMS_MSGCHRSET', 'lat')
        app.config.setdefault('SKYSMS_MSGENCODING', 'utf-8')

        for option in ['USERNAME', 'PASSWORD']:
            if app.config['SKYSMS_{0}'.format(option)] is None:
                raise ValueError('SKYSMS_{0} cannot be None!'.format(option))

        if app.config['SKYSMS_LOGFILE'] is not None:
            logging.basicConfig(filename=app.config['SKYSMS_LOGFILE'],
                                filemode='a+',
                                format="%(levelname)s (%(asctime)s): %(message)s",
                                datefmt='%m/%d/%Y %I:%M:%S %p',
                                level=logging.INFO)
        else:
            logging.basicConfig(format="%(levelname)s (%(asctime)s): %(message)s",
                                datefmt='%m/%d/%Y %I:%M:%S %p',
                                level=logging.INFO)
            logging.warning('log file was not specified')

    def send_message(self, phone_number, message):
        logging.info('Sending request to sms service')
        response = requests.get(SUBMIT_SM,
                                params={'login': current_app.config['SKYSMS_USERNAME'],
                                        'passwd': current_app.config['SKYSMS_PASSWORD'],
                                        'destaddr': phone_number,
                                        'msgchrset': current_app.config['SKYSMS_MSGCHRSET'],
                                        'msgtext': message.encode(current_app.config['SKYSMS_MSGENCODING'])})
        if not response.ok:
            logging.error('Some problem has occurred with sent request. '
                          'HTTP status: {code} {reason}'.format(code=response.status_code,
                                                                reason=response.reason))
            return False
        result = self._parse_response_text(response.text)
        if result[RETURNCODE] == SUCCESS_CODE:
            logging.info("{code} {value}".format(code=result[RETURNCODE], value=CODEVALUE[result[RETURNCODE]]))
            return True
        else:
            logging.error("{code} {value}".format(code=result[RETURNCODE], value=CODEVALUE[result[RETURNCODE]]))
            return False

    def send_password(self, phone_number, login, password):
        message = current_app.config['SKYSMS_PASSWORD_MESSAGE'] % {'login': login, 'password': password}
        return self.send_message(phone_number, message)

    @staticmethod
    def _parse_response_text(text):
        return {key: value.strip('\r') for key, value in [pair.split('=') for pair in text.strip().split('\n')]}
