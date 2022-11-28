import json
import Fname
import datetime


class Config:
    def __init__(self, fname):
        self.raw_json = json.load(open(fname, 'rb'))

    def exists(self, key):
        return key in self.raw_json

    def get(self, key, time=None):
        if time is None:
            time = datetime.datetime.now()

        return Fname.render(self.raw_json[key], time)

    def get_nothrow(self, key, time=None):
        try:
            return self.get(key, time)
        except:
            return None
