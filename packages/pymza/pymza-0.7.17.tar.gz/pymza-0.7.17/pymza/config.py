import os
import sys
import ConfigParser

from cached_property import cached_property

from .task import Task


class Config(object):

    def __init__(self, config_paths=None, debug=False):
        self.debug = debug
        self.config = ConfigParser.SafeConfigParser()

        for config_path in config_paths:
            self._read_config(config_path)

        self.home = os.path.abspath(
            os.path.dirname(config_paths and config_paths[0] or '.'))

    def _read_config(self, path):
        with open(path) as f:
            self.config.readfp(f)

    def add_home_to_pythonpath(self):
        sys.path.append(self.home)

    @property
    def kafka_hosts(self):
        return [x.strip() for x in self.config.get('DEFAULT', 'kafka_hosts').split(',')]

    def load_task(self, name):
        task_path = self.config.get(name, 'task')
        module = import_string(task_path)
        return Task(name, module)

    def tasks(self):
        return [x.strip() for x in self.config.sections() if
                (not self.config.has_option(x, 'disabled')
                 or not self.config.getboolean(x, 'disabled'))]

    def task_config(self, name):
        return dict(self.config.items(name))

    def state_dir(self):
        path = self.config.get('DEFAULT', 'state_dir')

        return os.path.join(self.home, path)

    @cached_property
    def serializer(self):
        try:
            serializer_module = self.config.get('DEFAULT', 'serializer')
        except ConfigParser.NoOptionError:
            serializer_module = 'json'
        module = import_string(serializer_module)

        assert hasattr(module, 'loads') and hasattr(
            module, 'dumps'), 'Serializer should have loads and dumps methods'

        return module


def import_string(path):
    if '.' not in path:
        return __import__(path)
    else:
        mod_path, mod_name = path.rsplit('.', 1)
    _temp = __import__(mod_path, None, None, [mod_name], -1)
    try:
        return getattr(_temp, mod_name)
    except AttributeError as e:
        raise ImportError(e)
