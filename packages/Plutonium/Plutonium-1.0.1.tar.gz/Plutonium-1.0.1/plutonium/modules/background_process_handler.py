
import os
import time
import subprocess
from signal import SIGTERM

from tools import SimpleResponse

from logger import get_logger
logger = get_logger(__name__)

class BackgroundProcessHandler(object):
    def __init__(self, command, pid_file):
        self.pid_file = pid_file
        self.command = command

    def start(self):
        if self.is_running():
            return SimpleResponse(False, 'Plutonium is already running. Pid: %d' % self.get_pid())

        pid = subprocess.Popen(self.command).pid

        file(self.pid_file,'w+').write("%s\n" % pid)

        return SimpleResponse(True, 'Started (pid: %s)' % pid)

    def get_pid(self):
        pid = None

        try:
            with open(self.pid_file, 'r') as f:
                try:
                    pid = int(f.read().strip())
                except TypeError as e:
                    pid = None
        except IOError:
            pid = None

        return pid

    def is_running(self):
        pid = self.get_pid()

        if pid is None:
            return False

        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def status(self):
        return SimpleResponse(True, 'Daemon is ' + ('running' if self.is_running() else 'not running'))

    def stop(self):
        # Get the pid from the pidfile
        pid = self.get_pid()

        if not pid:
            message = "Pidfile %s does not exist" % self.pid_file
            logger.error(message)
            return SimpleResponse(False, 'Daemon is not running')

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
            else:
                logger.error(err)
                sys.exit(1)

        return SimpleResponse(True, 'Daemon is stopped')

    def restart(self):
        self.stop()
        return self.start()
