import logging
import os
from pathlib import Path

os.chdir(Path(__file__).parent)
from datetime import datetime

# pylint: disable=C0413
from DjangoSite.wsgi import application

# cspell: disable-next-line
from paste.translogger import TransLogger
from waitress import serve

if __name__ == "__main__":
    logging.getLogger("waitress").setLevel(logging.WARNING)
    logApp = TransLogger(application, logging.getLogger("django"))
    print(
        f"""
Waitress Serving Django App
{datetime.now()}
http://127.0.0.1:8000      
"""
    )
    serve(logApp, port="8000", threads=6)
