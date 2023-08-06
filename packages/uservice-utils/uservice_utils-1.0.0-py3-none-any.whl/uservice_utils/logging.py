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

    if logstash_config and 'logstash' in logstash_config:
        root_logger.addHandler(
            logstash.LogstashHandler(
                config['logstash']['host'],
                int(config['logstash']['port']),
                int(config['logstash']['version'])
            )
        )
