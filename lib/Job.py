import os
import Fname
import pytz
import datetime


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
    return eval(dep_type, *kwargs)


class Job:
    def __init__(self, name, start_time, provides, end_time=None):
        assert(type(provides) == type(dependency))

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
            raise AssertionError('would_run muts be called with tz aware dt')

        if self.provides.exists(time):
            return False

        now = datetime.datetime.now()
        if now < self.start_time:
            return False

        if self.end_time and now > self.end_time:
            return False

        if self.dependencies:
            for dep in self.dependencies:
                if not dep.exists(time):
                    return False

        return True


def create_datetime(dtstr, timezone):
    timezone = pytz.timezone(timezone)
    dt = datetime.datetime.strptime(dtstr, '%H%m%s')
    return timezone.localize(dt)


def create_job_from_config(config):
    name = config.get('name')
    timezone_str = config.get('timezone')
    start_dt = create_datetime(config.get('start_time'), timezone_str)

    # for now all provides are files
    provides = create_dependency('file_dependency', config.get('provides_fname'))
    end_dt = None
    if config.exists('end_time'):
        end_dt = create_datetime(config.get('end_time'), timezone_str)

    job = Job(name, start_dt, provides, end_dt)
    if config.exists('dependencies'):
        deps = config.get('dependencies')
        for dep in deps:
            job.add_dependency(create_dependency(dep['type'], dep))

    return job
