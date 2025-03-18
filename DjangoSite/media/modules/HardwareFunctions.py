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
    subprocess.call(["shutdown", "-r", "-t", "0"])


class KillRedirect(HttpResponseRedirect):

    def close(self):
        super().close()
        LOGGER.info("Ending Process....")
        os.kill(os.getpid(), signal.SIGTERM)


def PullRepo():
    os.chdir(Path(__file__).parent.parent.parent)
    subprocess.call(["git", "pull", "origin"])


def SelfCommit():
    os.chdir(Path(__file__).parent.parent.parent)
    subprocess.call(["git", "add", "--all"])
    subprocess.call(["git", "commit", "-m", f'"Auto-Commit {datetime.date}"'])
