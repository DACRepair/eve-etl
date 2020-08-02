import os
from configparser import ConfigParser


class AppConfig:
    def __init__(self, config_path: str = None):
        self._config = ConfigParser()
        defaults = {}
        if config_path is None:
            for section, options in defaults.items():
                self._config.add_section(section)
                for option, value in options:
                    self._config.set(section, option, value)
        else:
            if os.path.isfile(config_path):
                self._config.read(config_path)
            else:
                raise KeyError("{} is not a valid config file.")

    def _gen_env(self, section: str, option: str):
        return "{}__{}".format(section.upper(), option.upper())

    def get(self, section: str, option: str, default: [str, None] = None) -> str:
        env_var = self._gen_env(section, option)
        env_var = os.getenv(env_var, default=self._config.get(section, option, fallback=default))
        return str(env_var)

    def getint(self, section: str, option: str, default: [int, None] = None) -> int:
        env_var = self._gen_env(section, option)
        env_var = os.getenv(env_var, default=self._config.getint(section, option, fallback=default))
        return int(env_var)

    def getboolean(self, section: str, option: str, default: [bool, None] = None) -> bool:
        env_var = self._gen_env(section, option)
        env_var = os.getenv(env_var, default=self._config.get(section, option, fallback=default))
        return str(env_var).lower() in ['true', '1']

    def getfloat(self, section: str, option: str, default: [float, None] = None) -> float:
        env_var = self._gen_env(section, option)
        env_var = os.getenv(env_var, default=self._config.getfloat(section, option, fallback=default))
        return float(env_var)

    def options(self, section: str):
        envs = [x for x in os.environ if x.startswith("{}__".format(section).upper())]
        if len(envs) > 0:
            return [x.rstrip("{}__".format(section).upper()).lower() for x in envs]
        else:
            return self._config.options(section)


_path = os.path.normpath("{}/{}".format(os.getcwd(), "config.ini"))
if os.getenv("CONFIG_PATH", default=None) is not None:
    _path = os.path.normpath(os.getenv("CONFIG_PATH", default=None))
config = AppConfig(config_path=_path)
