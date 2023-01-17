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
        self.config = Config.Config(config_fname)
        self.var_dir = self.config.get('var_dir')
        self.logger = Logger.create(__name__, filename=self.config.get('log_fname'))
        self.logger.info('config_fname=' + config_fname)

        self.state = shelve.open(self.config.get('store_fname'))
        self._init_jobs(self.config.get('job_config_dir'))

    def __del__(self):
        self.state.close()

    def _init_jobs(self, job_config_dir):
        jobs = Job.create_jobs(job_config_dir)
        names = set([j.name for j in jobs])
        if len(jobs) != len(names):
            raise AssertionError('duplicate names in job description')

        for job in jobs:
            name = job.name

            if name in self.state:
                # update existing
                self.logger.info('updating job name=%s old=%s new=%s' % (name, str(self.state[name]), str(job)))
                self.state[name].start_time = job.start_time
                self.state[name].provides = job.provides
                self.state[name].end_time = job.end_time
                self.state[name].dependencies = job.dependencies
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

        state = self.state[name]

        if state.would_run(time):
            if dryrun:
                self.logger.info('dryrun name=%s state=%s' % (name, str(state)))
            else:
                self.run_task(state)

    def run_task(self, state):
        def run_background(job_state):
            try:
                with FileLock(os.path.join(self.var_dir, job_state.name+'.lock')):
                    self.logger.info('run name=%s state=%s' % (job_state.name, str(job_state)))
                    # TODO - run the command
                    job_state.last_run = current_time()
            except FileLockException:
                self.logger.warn('job name=%s failed to acquire job lock' % (job_state.name))

        t1 = threading.Thread(target=run_background, args=[state])
        t1.start()
