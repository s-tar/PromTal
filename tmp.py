from application import create_app
from application.models.news import News
from application.models.user import User

app = create_app('default')
with app.app_context():
    user = User.query.get_or_404(817)
    print(len(user.news))
    # print(user_news)
    # print(user_news.to_json().data)