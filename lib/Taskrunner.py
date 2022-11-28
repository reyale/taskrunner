import shelve
import Config


class Taskrunner:

    def __init__(self, config_fname):
        self.state = None
        self.config = Config.Config(config_fname)
        self._init_store(self.config.get('store_fname'))
        self._init_jobs(self.config.get('job_config'))

    def __del__(self):
        self.state.close()

    def _init_store(self, store_fname):
        self.state = shelve.open(store_fname)

    def _init_jobs(self, job_config):
        pass

    def run(self, time):
        pass

    def run_one(self, time, job_name):
        pass
