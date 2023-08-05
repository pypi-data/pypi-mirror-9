import socket
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import sys

from base import Base
from database import Job, Log
from notification import Notification
from filelock import FileLock, FileLocked


class Cron(Base):
    job = None
    log = None

    def __init__(self):
        super(Cron, self).__init__()
        self.log = Log()

    def run(self, name):
        self.log.starttime = datetime.now()

        try:
            self.job = Job.get(Job.name == name)
            self.jobname = name
            self.log.job = self.job
            self.log.server = socket.gethostname()
            self.debug("started", "command: %s" % self.job.command, "started at: %s" % self.log.starttime)

            self._execute()
        except Job.DoesNotExist:
            self.logger.error("Job %s does not exist" % name)
            sys.exit(1)
        except Exception, e:
            self.log.error = e
            self.log.status = "failed"

        if self.log.error is not None:
            self.logger.error(self.log.error)

        self.log.endtime = datetime.now()
        runtime = self.log.endtime - self.log.starttime

        if self.log.status is None:
            if self.log.returncode != 0:
                self.log.status = "failed"
            else:
                self.log.status = "ok"

        self.log.save()
        self.debug("ended at: %s" % self.log.endtime, "runtime: %s" % str(runtime), "status: %s" % self.log.status)

        if self.job.notify:
            self.debug("sending notifications")
            notification = Notification(self.log)
            notification.send()

        self.debug("finished")

    def _execute(self, nolock=False):
        try:
            if self.job.locking and not nolock:
                lock = FileLock("/tmp/%s" % self.job.name)
                self.debug("locking enabled, lockfile: %s" % lock.lockfname)
                with lock:
                    return self._execute(not nolock)

            process = Popen(self.job.command, shell=True, stdout=PIPE, stderr=STDOUT)
            self.log.output, self.log.error = process.communicate()
            self.log.returncode = process.poll()
            self.debug("return code: %s" % self.log.returncode, "output:\n%s" % self.log.output)
        except FileLocked:
            self.log.error = "job is currently running, or lockfile has not been removed"
            self.log.status = "lock"
        except Exception, e:
            self.log.error = e
            self.log.status = "failed"

