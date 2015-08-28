from flask import render_template, render_template_string
from envelopes import Envelope

from application.celery import celery
from application.models.user import User
from application.mail_sender import gmail

# TODO Resolve problem with sending html in email
restore_password = u"Для восстановления пароля пройдите по ссылке: http://reimu.uaprom{{ url_for('password.restore_pass', token=token) }}"
news_notification = u"Новая новость на портале: http://reimu.uaprom{{ url_for('news.news_one', id=id) }} ({{ title }})"


@celery.task()
def send_news_notification(news_id, news_title):
    users = User.query.filter_by(news_notification=True).all()
    for user in users:
        envelope = Envelope(
            from_addr=(u'promtal.ua@gmail.com', u'PromTal'),
            to_addr=(user.email, user.full_name),
            subject=u'Новая новость',
            # text_body=render_template('email/news_notification.html', id=news_id, title=news_title),
            text_body=render_template_string(news_notification, id=news_id, title=news_title),
        )
        envelope.add_header("Content-Type", "text/html")
        gmail.send(envelope)


@celery.task()
def send_password_restore_ref(email, name, token):
    envelope = Envelope(
        from_addr=(u'promtal.ua@gmail.com', u'PromTal'),
        to_addr=(email, name),
        subject=u'Восстановление пароля',
        # text_body=render_template('email/password_restore.html', token=token),
        text_body=render_template_string(restore_password, token=token),
    )
    print(envelope)
    envelope.add_header("Content-Type", "text/html")
    gmail.send(envelope)
