import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from waitress import serve  # type:ignore

os.chdir(Path(__file__).parent)

# pylint: disable=C0413
from DjangoSite.asgi import application as asgi_app
from DjangoSite.wsgi import application as wsgi_app


def RunASGI():
    application = asgi_app
    print(f"Uvicorn Serving Django App\n{datetime.now()}\nhttp://127.0.0.1:8080")
    uvicorn.run(application, host="0.0.0.0", port=8080, log_config=None)
    return 0


def RunWSGI():
    application = wsgi_app
    logging.getLogger("waitress").setLevel(logging.WARNING)
    print(f"Waitress Serving Django App\n{datetime.now()}\nhttp://127.0.0.1:8080")
    serve(application, host="0.0.0.0", port=8080, threads=4)
    return 0


if __name__ == "__main__":
    USE_ASGI = True if len(sys.argv) < 2 else sys.argv[1] == "True"
    _RESULT = RunASGI() if USE_ASGI else RunWSGI()
