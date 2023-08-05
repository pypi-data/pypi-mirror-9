import os
import sys
from ConfigParser import SafeConfigParser

from .task import Task

class Config(object):
    def __init__(self, config_path=None, debug=False):
        self.home = os.path.abspath(os.path.dirname(config_path or '.'))
        self.debug = debug
        self.config = SafeConfigParser()
        with open(config_path) as f:
            self.config.readfp(f)

    def add_home_to_pythonpath(self):
        sys.path.append(self.home)

    @property
    def kafka_hosts(self):
        return [x.strip() for x in self.config.get('DEFAULT', 'kafka_hosts').split(',')]

    def load_task(self, name):
        task_path = self.config.get(name, 'task')
        module = import_task(task_path)
        return Task(name, module)

    def tasks(self):
        return [x.strip() for x in self.config.sections()]

    def task_config(self, name):
        return dict(self.config.items(name))

    def state_dir(self):
        path = self.config.get('DEFAULT', 'state_dir') or './state'
        return os.path.join(self.home, path)


def import_task(path):
    if '.' not in path:
        return __import__(path)
    else:
        mod_path, mod_name = path.rsplit('.', 1)
    _temp = __import__(mod_path, None, None, [mod_name], -1)
    try:
        return getattr(_temp, mod_name)
    except AttributeError as e:
        raise ImportError(e)