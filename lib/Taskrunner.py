import shelve
import Config
from dateutil.tz import tzlocal
import datetime
import Logger


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
        self.logger = Logger.create(__name__, filename=self.config.get('log_fname'))
        self.logger.info('config_fname=' + config_fname)

        self.state = shelve.open(self.config.get('store_fname'))
        self._init_jobs(self.config.get('job_config'))

    def __del__(self):
        self.state.close()

    def _init_jobs(self, job_config):
        pass

    def run(self, time, dryrun=False):
        for name, state in self.state:
            self.run_one(time, dryrun)

    def run_one(self, name, time, dryrun=False):
        if name not in self.state:
            return

        state = self.state[name]

        if state.would_run(time):
            if dryrun:
                self.logger.info('dryrun name=%s state=%s' % (name, str(state)))
            else:
                self.logger.info('run name=%s state=%s' % (name, str(state)))
