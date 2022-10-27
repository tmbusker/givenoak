echo off

call activate

@REM django-admin runserver [addrport]
@REM python manage.py runserver --noreload
python manage.py runserver
