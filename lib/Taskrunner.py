import os
import shelve
import threading
import Config
from dateutil.tz import tzlocal
import datetime
import Logger
import Job
from filelock import FileLock, FileLockException

_time_format = '%H:%M:%S'


class State:
    def __init__(self, job):
        self.last_run = None
        self.job = job


def current_time():
    return datetime.datetime.now(tzlocal())


def parse_time(time_str, tz=tzlocal()):
    res = datetime.datetime.strtime(_time_format)
    res = res.replace(tzinfo=tz)
    return res


class Taskrunner:

    def __init__(self, config_fname):
        self.threads = []  # at most we have the number of threads as jobs
        self.config = Config.Config(config_fname)
        self.var_dir = self.config.get('var_dir')
        self.logger = Logger.create(__name__, filename=self.config.get('log_fname'))
        self.logger.info('taskrunner start config_fname=%s var_dir=%s' % (config_fname, self.var_dir))

        self.state = shelve.open(self.config.get('store_fname'))
        self._init_jobs(self.config.get('job_config_dir'))

    def stop(self):
        for t in self.threads:
            t.join()

        self.state.close()

    def _init_jobs(self, job_config_dir):
        jobs = Job.create_jobs(job_config_dir)
        names = set([j.name for j in jobs])
        if len(jobs) != len(names):
            raise AssertionError('duplicate names in job description')

        for job in jobs:
            name = job.name

            if name in self.state:
                if job == self.state[name]:
                    self.logger.info('no update job={}'.format(job.name))
                    continue

                # update existing
                self.logger.info('updating job name=%s \nold=%s \nnew=%s' % (name, str(self.state[name]), str(job)))
                job.last_run = self.state[name].last_run
                self.state[name] = job
                # intentionally not updating last run
            else:
                self.state[name] = job
                self.logger.info('loading new job %s' % str(job))

    def run(self, time, dryrun=False):
        for name, state in self.state.items():
            self.run_one(name, time, dryrun)

    def run_one(self, name, time, dryrun=False):
        if name not in self.state:
            return

        if self.state[name].would_run(time):
            if dryrun:
                self.logger.info('dryrun name=%s state=%s' % (name, self.state[name]))
            else:
                self._run_task(name)

    def _run_background(self, name):
        try:
            with FileLock(os.path.join(self.var_dir, name + '.lock')):
                self.logger.info('run name=%s state=%s' % (name, str(self.state[name])))
                # TODO - run the command
                state = self.state[name]
                state.last_run = current_time()
                self.state[name] = state
        except FileLockException:
            self.logger.warn('job name=%s failed to acquire job lock' % (name))

    def _run_task(self, name):
        self.threads.append(threading.Thread(target=self._run_background, args=(name,)))
        self.threads[-1].start()
