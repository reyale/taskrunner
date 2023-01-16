import logging


_seen = {}


def get_handler(type_name, kwargs):
    if type_name == 'stream':
        return logging.StreamHandler
    elif type_name == 'file':
        return logging.FileHandler(kwargs.get('filename'))
    else:
        raise AssertionError('no valid type of handler with type_name=' + type_name)


def get_level(level):
    return logging.__dict__[level]


class Logger(logging.Logger):
    def __init__(self, name, **kwargs):
        if name in _seen:
            raise AssertionError('you tried to create a logger twice with name=' + name)

        self.logger = logging.getLogger(name)
        handler = get_handler(kwargs.get('type', 'file'), kwargs)
        handler.setLevel(get_level(kwargs.get('level', 'DEBUG')))

        format_str = kwargs.get('format_string', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical


def create(name, **kwargs):
    if name in _seen:
        return _seen[name]

    logger = Logger(name, **kwargs)
    _seen[name] = logger
    return logger


def get(name):
    return _seen[name]
