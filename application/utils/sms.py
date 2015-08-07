import requests
import logging

from flask import current_app

logger = logging.getLogger("sms")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt="%(name)s:%(levelname)s - - [%(asctime)s] %(message)s",
                              datefmt='%y/%b/%d %H:%M:%S')

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
            file_handler = logging.FileHandler(filename=app.config['SKYSMS_LOGFILE'])
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
            logger.warning('log file was not specified')

    def send_message(self, mobile_phone, message):
        logger.info('Sending request to sms service')
        response = requests.get(SUBMIT_SM,
                                params={'login': current_app.config['SKYSMS_USERNAME'],
                                        'passwd': current_app.config['SKYSMS_PASSWORD'],
                                        'destaddr': mobile_phone,
                                        'msgchrset': current_app.config['SKYSMS_MSGCHRSET'],
                                        'msgtext': message.encode(current_app.config['SKYSMS_MSGENCODING'])},
                                timeout=5)
        if not response.ok:
            logger.error('Some problem has occurred with sent request. '
                          'HTTP status: {code} {reason}'.format(code=response.status_code,
                                                                reason=response.reason))
            return False
        result = self._parse_response_text(response.text)
        if result[RETURNCODE] == SUCCESS_CODE:
            logger.info("{code} {value}".format(code=result[RETURNCODE], value=CODEVALUE[result[RETURNCODE]]))
            return True
        else:
            logger.error("{code} {value}".format(code=result[RETURNCODE], value=CODEVALUE[result[RETURNCODE]]))
            return False

    def send_password(self, mobile_phone, login, password):
        message = current_app.config['SKYSMS_PASSWORD_MESSAGE'] % {'login': login, 'password': password}
        return self.send_message(mobile_phone, message)

    @staticmethod
    def _parse_response_text(text):
        return {key: value for key, value in [pair.split('=') for pair in text.splitlines()]}
