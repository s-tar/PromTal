from flask import render_template

from application.celery import celery
from application.models.user import User
from application.mail_sender import send_mail


@celery.task()
def send_news_notification(news_id, news_title):
    for user in User.query.filter(news_notification=True).all():
        send_mail(user.email,
                  render_template('email/news_notification.html', id=news_id, title=news_title))
