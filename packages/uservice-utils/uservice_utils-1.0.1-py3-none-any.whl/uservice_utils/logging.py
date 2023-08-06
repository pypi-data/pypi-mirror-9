# uservice-utils
# Copyright (C) 2015 Canonical
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Code to configure logging for micro-services."""

import collections
import logging
import logging.handlers
import os

__all__ = [
    'configure_service_logging'
]


def configure_service_logging(log_file_path, logstash_config=None):
    """Configure python's logging for the micro-service.

    This function sets a standard level of logging for all our services. The
    default setups is to log to a file, or stderr if the file directory cannot
    be created.

    Additionally, if the logstash config is supplied, a logstash handler will
    be configured.

    :param log_file_path: The full path to a file to be used for logging. If
        the file's directory does not exist, this function will fall back to
        logging to stderr instead of the file.
    :param logstash_config: If specified, must be a mapping type that contains
        the keys 'host', 'port', and 'version'.

    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Silence requests logging, which is created by nova, keystone and swift.
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)

    # If there is no .directory for the file, fall back to stderr logging
    log_dir = os.path.dirname(log_file_path)
    if os.path.exists(log_dir):
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file_path,
            when='D',
            interval=1
        )
    else:
        print("'logs' directory '{}' does not exist, using stderr "
              "for app log.".format(log_dir))
        handler = logging.StreamHandler()

    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s  %(name)s %(levelname)s: %(message)s'
        )
    )
    root_logger.addHandler(handler)

    if logstash_config:
        root_logger.addHandler(
            logstash.LogstashHandler(
                logstash_config['host'],
                int(logstash_config['port']),
                int(logstash_config['version'])
            )
        )


class ExtraLogger(logging.Logger):

    """A logger that handles passing 'extra' arguments to all logging calls.

    Tired of having to write:

    logger.info("Some message", extra=extra)

    ... everywhere?

    Now you can install this class as the Logger class:

    >>> import logging
    >>> logging.setLoggerClass(ExtraLogger)

    Then, to use it, get your logger as usual:

    >>> logger = logging.getLogger(__name__)

    ...and set your extra arguments once only:

    >>> logger.set_extra_args(dict(foo='bar', baz='123'))

    And those arguments will be included in all normal log messages:

    >>> logger.info("Hello World") # message will contain extra args set above

    Extra arguments can be passed to individual logging calls, and will take
    priority over any set with the set_extra_args call.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._extra_args = dict()

    def set_extra_args(self, extra_args):
        """Set the 'extra' arguments you want to be passed to every log message.

        :param extra_args: A mapping type that contains the extra arguments you
            want to store.
        :raises TypeError: if extra_args is not a mapping type.

        """
        if not isinstance(extra_args, collections.Mapping):
            raise TypeError("extra_args must be a mapping")
        self._extra_args = extra_args

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, user_extra=None, sinfo=None):
        extra = self._extra_args.copy()
        if user_extra:
            extra.update(user_extra)
        return super().makeRecord(name, level, fn, lno, msg, args, exc_info,
                                  func, extra, sinfo)


