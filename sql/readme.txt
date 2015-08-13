Теперь миграции проходят так:

python manage.py db migrate
python clean_migration.py
python manage.py db upgrade

Надо создавать вьюхи в БД командой:
sudo -u postgres psql promtal
