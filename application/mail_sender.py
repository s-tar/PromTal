from envelopes import Envelope, GMailSMTP

def send_mail(to_mail):
    envelope = Envelope(
        from_addr=(u'promtal.ua@gmail.com', u'From Example'),
        to_addr=(to_mail, u'To Example'),
        subject=u'Envelopes demo',
        text_body=u"I'm a helicopter!"
    )
    gmail = GMailSMTP('promtal.ua@gmail.com', '314promtal.ua')
    gmail.send(envelope)