import shelve
import Config
from dateutil.tz import tzlocal
import datetime


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
        self.state = shelve.open(self.config.get('store_fname'))
        self._init_jobs(self.config.get('job_config'))

    def __del__(self):
        self.state.close()

    def _init_jobs(self, job_config):
        pass

    def run(self, time, dryrun=False):
        for name, state in self.state:
            if state.would_run(time):
                if dryrun:
                    print('dryrun', name, state)
                else:
                    print('run', name, state)

    def run_one(self, time, job_name):
        pass
