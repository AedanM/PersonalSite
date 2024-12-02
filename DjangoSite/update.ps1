Set-Variable fileToUp=%1
# cspell: disable-next-line
python .\manage.py makemigrations %fileToUp%
Set-Variable /p "id=Enter Migration ID: "
# cspell: disable-next-line
python .\manage.py sqlmigrate %fileToUp% %id%
python .\manage.py check
Set-Variable /p "proceed=Proceed with Update (y/N)? "
if (%proceed% == y) {
    python .\manage.py migrate
}
