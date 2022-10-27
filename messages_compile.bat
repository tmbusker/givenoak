echo off

call activate

python manage.py compilemessages -f %*
