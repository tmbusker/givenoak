echo off

call activate

set DJANGO_SUPERUSER_PASSWORD=p09olp09ol
set DJANGO_SUPERUSER_EMAIL=yujiwen@hotmail.com

python manage.py createsuperuser --no-input --username admin
