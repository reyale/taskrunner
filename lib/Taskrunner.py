import shelve
import Config


class Taskrunner:

    def __init__(self, config_fname):
        self.config = Config.Config(config_fname)
        self.state = shelve.open(self.config.get('store_fname'))
        self._init_jobs(self.config.get('job_config'))

    def __del__(self):
        self.state.close()

    def _init_jobs(self, job_config):
        pass

    def run(self, time):
        pass

    def run_one(self, time, job_name):
        pass
