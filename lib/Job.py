import os
import Fname


class dependency:
    def exists(self, time):
        return True


class file_dependency(dependency):
    def __init__(self, fname):
        self.fname = fname

    def exists(self, time):
        return os.path.exists(Fname.render(self.fname, time))


class Job:
    def __init__(self, name, timezone, start_time, provides, end_time=None):
        assert(type(provides) == type(dependency))

        self.name = name
        self.timezone = timezone
        self.start_time = start_time
        self.provides = provides
        self.end_time = end_time

    def add_provides(self, provide):
        pass

    def would_run(self, time):
        pass
