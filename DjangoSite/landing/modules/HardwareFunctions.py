import datetime
import logging
import os
import signal
import subprocess
import time
from pathlib import Path

from django.http import HttpResponseRedirect

LOGGER = logging.getLogger("UserLogger")


def RebootPC():
    pass  # subprocess.call(["shutdown", "-r", "-t", "0"])


class KillRedirect(HttpResponseRedirect):

    def close(self):
        super().close()
        LOGGER.info("Ending Process....")
        time.sleep(0.5)
        os.kill(os.getpid(), signal.SIGTERM)


def PullRepo():
    os.chdir(Path(__file__).parent.parent.parent)
    results = subprocess.check_output(["git", "pull", "origin", "main"])
    LOGGER.info("Pulled from Git: %s", str(results))


def SelfCommit():
    os.chdir(Path(__file__).parent.parent.parent)
    subprocess.call(["git", "add", "--all"])
    subprocess.call(["git", "commit", "-m", f'"Auto-Commit {datetime.date}"'])
