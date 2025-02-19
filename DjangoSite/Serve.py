import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from waitress import serve

os.chdir(Path(__file__).parent)

# pylint: disable=C0413
from DjangoSite.asgi import application as asgi_app
from DjangoSite.wsgi import application as wsgi_app

# cspell: disable-next-line
from paste.translogger import TransLogger

if __name__ == "__main__":
    USE_ASGI = True if len(sys.argv) < 2 else sys.argv[1]
    if USE_ASGI:
        application = asgi_app
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        uvicorn.run(application, host="0.0.0.0", port=8080)
    else:
        application = wsgi_app
        logging.getLogger("waitress").setLevel(logging.WARNING)
        logApp = TransLogger(application, logging.getLogger("django"))
        print(f"Waitress Serving Django App\n{datetime.now()}\nhttp://127.0.0.1:8080")
        serve(application, host="0.0.0.0", port=8080)
