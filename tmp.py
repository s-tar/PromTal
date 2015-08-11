from application import create_app
from application.utils.datagen import generate_inner_phone

app = create_app('default')
with app.app_context():
    print(generate_inner_phone(6000, 9999))