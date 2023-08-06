import util
from flask import Flask
from os.path import expanduser
from pkgutil import extend_path
from werkzeug.exceptions import default_exceptions
import os

__path__ = extend_path(__path__, __name__)


class Meh(object):
    def __init__(self, name=None, config={}):
        self._module = name.split('.')[-1]

        self.app = Flask(self._module)
        self.app.config.update(**config)

        self._load_config()
        self._configure_logging()


    def _load_config(self):
        """
        Override app.config from externalized config files. First checks in user's
        homedir then at the system level in /etc/.
        """
        _home_path = expanduser(
            '~/.config/podhub/{}/config.py'.format(self._module))
        _system_path = '/etc/podhub/{}/config.py'.format(self._module)

        if os.access(_home_path, os.R_OK):
            self.app.config.from_pyffile(_home_path, silent=True)
        elif os.access(_system_path, os.R_OK):
            self.app.config.from_pyffile(_system_path, silent=True)

    def _configure_logging(self):
        """
        Set up basic file logging.
        """
        if not self.app.debug:
            from logging import FileHandler
            import logging

            _log_path = '/var/log/podhub/{}/app.log'.format(self._module)
            file_handler = FileHandler(
                self.app.config.get('LOG_FILE', _log_path))
            file_handler.setLevel(
                getattr(logging, self.app.config.get('LOG_LEVEL', 'WARNING')))
            self.app.logger.addHandler(file_handler)

    def _log_errors(self):
        """
        Configure json-formatted error logging.
        """
        for code in default_exceptions.iterkeys():
            self.app.error_handler_spec[None][code] = util.make_json_error
