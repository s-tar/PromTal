from envelopes import Envelope, GMailSMTP


def send_mail_restore_pass(to_mail, token):
    text = u"Ссылка для восстановления пароля http://reimu.uaprom/password/restore/{token}".format(token=token)
    send_mail(to_mail, text)


def send_mail(to_mail, text):
    envelope = Envelope(
        from_addr = (u'promtal.ua@gmail.com', u'From Example'),
        to_addr = (to_mail, u'To Example'),
        subject = u'Envelopes demo',
        text_body = text
    )
    gmail = GMailSMTP('promtal.ua@gmail.com', '314promtal.ua')
    gmail.send(envelope)