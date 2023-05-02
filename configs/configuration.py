import os

from configs.utils import str2bool


class Configuration:

    def __init__(self):
        self._read_config()

    _dir_path = os.path.dirname(os.path.realpath(__file__))
    _path = os.path.join(_dir_path, '../params.conf')
    _conf_dict = {}

    def _read_config(self):
        with open(self._path, 'r', encoding='utf-8') as file:
            for line in file:
                line_clean = line.strip()
                idx = line_clean.find('=')
                if (idx <= 0) or (idx == (len(line_clean) - 1)):
                    raise ValueError('Provided configuration file contains incorrect strings.')

                key = line_clean[:idx]
                value = line_clean[idx + 1:]

                self._conf_dict[key] = value

    def _try_get_value(self, key, dtype_converter=None):
        if key not in self._conf_dict:
            raise ValueError(f'Provided configuration file has no param: {key}')

        value = self._conf_dict[key]
        if dtype_converter is None:
            return value

        try:
            value = dtype_converter(value)
        except Exception as exp:
            raise ValueError(f'Provided value for "{key}" param could not be cast to {dtype_converter}') from exp

        return value

    @property
    def text_size_limit(self):
        return self._try_get_value('text_size_limit', int)

    @property
    def text_size_threshold(self):
        return self._try_get_value('text_size_threshold', int)

    @property
    def extract_first_img_only(self):
        return self._try_get_value('extract_first_img_only', str2bool)

    @property
    def logger_name(self):
        return self._try_get_value('logger_name')

    @property
    def logger_level(self):
        levels = {
            'CRITICAL': 50,
            'FATAL': 50,
            'ERROR': 40,
            'WARNING': 30,
            'WARN': 30,
            'INFO': 20,
            'DEBUG': 10,
            'NOTSET': 0,
        }

        level: str = self._try_get_value('logger_level')
        if level.upper() not in levels:
            raise ValueError('Invalid logger level.')

        return levels[level]

    @property
    def dir_path(self):
        return self._dir_path
