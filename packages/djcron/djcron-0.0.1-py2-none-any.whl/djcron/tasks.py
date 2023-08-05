import os
import tempfile
import logging
import subprocess
import datetime
import socket
from pprint import pprint
from django.conf import settings

import celery

import psutil

from . import models

LOGGER = logging.getLogger(__name__)


def print_status(pid):
    p = psutil.Process(pid)
    pprint(p.as_dict())


@celery.task.task(name='Cron worker')
def djcron_worker(job_id, *args, **kwargs):
    """ Executes a Job as a shell command """

    LOGGER.debug('Retrieving the job')
    job = models.Job.objects.get(id=job_id)

    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    LOGGER.debug('Created temporal file %s', tmpfile.name)

    with open(tmpfile.name, 'w+') as fd:
        fd.write(job.script)

    execution = models.Execution(
        job=job,
        start=datetime.datetime.utcnow(),
        host=socket.getfqdn(),
    )
    execution.save()

    start = datetime.datetime.utcnow()
    command = "sh %s" % tmpfile.name
    LOGGER.debug('Executing %s', command)
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
        shell=True)

    rc = p.wait()
    end = datetime.datetime.utcnow()
    LOGGER.debug('End %s', command)

    stdout = p.stdout.read()
    stderr = p.stderr.read()
    #print start, end
    #print_status(p.pid)


    execution.rc = rc
    execution.start = start
    execution.end = end
    execution.stdout = stdout
    execution.stderr = stderr
    execution.save()

    os.unlink(tmpfile.name)

    return
