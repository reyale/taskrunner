import os
import Fname
import pytz
import datetime
import glob

import Config


class dependency:
    def exists(self, time):
        return True


class file_dependency(dependency):
    def __init__(self, fname):
        self.fname = fname

    def __str__(self):
        return 'type=%s fname=%s' % (__name__, self.fname)

    def exists(self, time):
        return os.path.exists(Fname.render(self.fname, time))


def create_dependency(dep_type, **kwargs):
    return globals()[dep_type](*kwargs)


class Job:
    def __init__(self, name, start_time, provides, end_time=None):
        assert(issubclass(type(provides), dependency))

        if start_time.tzinfo is None:
            raise AssertionError('start time must have tz aware dt')

        if end_time is not None and end_time.tzinfo is None:
            raise AssertionError('end time must have tz aware dt')

        self.name = name
        self.start_time = start_time
        self.provides = provides
        self.end_time = end_time
        self.dependencies = []

    def __str__(self):
        result = 'name=%s start_time=%s provides=%s end_time=%s' % (self.name, str(self.start_time), str(self.provides), str(self.end_time))
        for dep in self.dependencies:
            result += ' ' + str(dep)

        return result

    def add_dependency(self, provide):
        self.dependencies.append(provide)

    def would_run(self, time):
        if time.tzinfo is None:
            raise AssertionError('would_run must be called with tz aware dt')

        if self.provides.exists(time):
            return False

        if time < self.start_time:
            return False

        if self.end_time and time > self.end_time:
            return False

        if self.dependencies:
            for dep in self.dependencies:
                if not dep.exists(time):
                    return False

        return True


def create_datetime(dtstr, timezone):
    timezone = pytz.timezone(timezone)
    dt = datetime.datetime.strptime(dtstr, '%H:%M:%S')
    return timezone.localize(dt)


def create_job_from_config(config):
    name = config.get('name')
    timezone_str = config.get('timezone')
    start_dt = create_datetime(config.get('start_time'), timezone_str)

    # for now all provides are files
    provides = create_dependency('file_dependency', fname=config.get('provides_fname'))
    end_dt = None
    if config.exists('end_time'):
        end_dt = create_datetime(config.get('end_time'), timezone_str)

    job = Job(name, start_dt, provides, end_dt)
    if config.exists('dependencies'):
        deps = config.get('dependencies')
        for dep in deps:
            job.add_dependency(create_dependency(dep['type'], *dep))

    return job


def create_jobs(job_config_dir):
    job_config_fnames = glob.glob(job_config_dir + '/*.json')
    if len(job_config_fnames) <= 0:
        raise AssertionError('no jobs to load')

    results = []
    for fname in job_config_fnames:
        cfg = Config.Config(fname)
        results.append(create_job_from_config(cfg))

    return results
