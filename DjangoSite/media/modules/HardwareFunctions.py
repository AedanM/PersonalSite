import datetime
import logging
import os
import signal
import subprocess
import threading
import time
from pathlib import Path

LOGGER = logging.getLogger("UserLogger")


def RebootPC():
    subprocess.call(["shutdown", "-r", "-t", "0"])


def StartRestartThread(seconds):
    threading.Thread(target=RestartIn, args=[seconds]).start()


def RestartIn(seconds):
    time.sleep(seconds)
    LOGGER.info("Restarting....")
    os.kill(os.getpid(), signal.SIGTERM)


def PullRepo():
    os.chdir(Path(__file__).parent.parent.parent)
    subprocess.call(["git", "pull", "origin"])


def SelfCommit():
    os.chdir(Path(__file__).parent.parent.parent)
    subprocess.call(["git", "add", "--all"])
    subprocess.call(["git", "commit", "-m", f'"Auto-Commit {datetime.date}"'])
    StartRestartThread(1)
