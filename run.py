from beaker.middleware import SessionMiddleware
from application import app
from application.config import config

app.wsgi_app = SessionMiddleware(app.wsgi_app, config['session'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)