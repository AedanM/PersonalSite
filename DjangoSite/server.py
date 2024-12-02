import logging
import os
from pathlib import Path

os.chdir(Path(__file__).parent)

from DjangoSite.wsgi import application
from paste.translogger import TransLogger
from waitress import serve

if __name__ == "__main__":
    logging.getLogger("waitress").setLevel(logging.WARNING)
    logApp = TransLogger(application, logging.getLogger("django"))
    print(
        """
Waitress Serving Django App
http://127.0.0.1:8000      
"""
    )
    serve(logApp, port="8000", threads=16)
