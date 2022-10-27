echo off

call activate

if "%1" EQU "" (
    python manage.py makemigrations cmm
    python manage.py makemigrations mst
    python manage.py makemigrations jinji
) else (
    python manage.py makemigrations %*
)

python manage.py migrate
