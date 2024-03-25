@echo off

set fileToUp=%1

python .\manage.py makemigrations %fileToUp%
set /p "id=Enter Migration ID: "
python .\manage.py sqlmigrate %fileToUp% %id%
python .\manage.py check
set /p "proceed=Proceed with Update (y/N)? "
if %proceed% == y (
    python .\manage.py migrate
)
