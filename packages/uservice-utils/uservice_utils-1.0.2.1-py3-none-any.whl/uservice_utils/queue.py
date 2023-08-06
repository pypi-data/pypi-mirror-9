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

"""Code to abstract away rabbit message queues."""

import enum
import logging
from pdb import bdb

import kombu
from kombu.mixins import ConsumerMixin

logger = logging.getLogger(__name__)

__all__ = [
    'MessageActions',
    'SimpleRabbitQueueWorker',
    'RetryPolicy',
    'DefaultRetryPolicy',
]


class MessageActions(enum.Enum):

    """Actions that the message processing callback can request.

    These enum values can be returned from the message processing callback,
    and the CoreImagePublisherQueueMonitor will take appropriate action.

    """

    # The message needs to be retried. This might cause the message to be
    # retried, or it might reject the message if it's retry count has been
    # exceeded.
    Retry = 1

    # The message was processed properly, and should be acknowledged.
    Acknowledge = 2


class SimpleRabbitQueueWorker(ConsumerMixin):

    """A class that watches for incoming messages from a single queue, and calls
    a callback to process them.

    Note that this class does not deal with rabbitMQ exchanges - it only works
    with single, direct queues.

    """

    def __init__(self, connection, queue, on_message_cb, retry_policy):
        """Construct a new SimpleRabbitQueueWorker.

        The connection must be a kombu.Connection instance, but otherwise may
        be constructed to point at any backend (including a memory backend).

        The queue should be a single string, pointing to the queue you wish to
        monitor.

        The callback can be any callable, including a class with __call__
        defined. The callable must accept a single parameter, which will be
        the decoded message payload. The callable must also return one of the
        MessageActions attributes, and must not raise any uncaught exceptions.

        The retry policy should be an instance of RetryPolicy, or one of it's
        subclasses. The 'DefaultRetryPolicy' is a sensible policy that's been
        created for you already.

        :param connection: A kombu.Connection instance.
        :param queues: A list of rabbitMQ queue names.
        :param on_message_db: A callable that will be called for every new
            messages from the rabbitMQ queue(s).
        :param retry_policy: An instance of RetryPolicy, or it's subclass.

        """
        self.connection = connection
        self._queue = queue
        self.on_message_cb = on_message_cb
        self.retry_policy = retry_policy

    def get_consumers(self, Consumer, channel):
        """Return consumers instances for all configured queues."""
        queues = [ kombu.Queue(self._queue) ]
        return [Consumer(queues=queues, callbacks=[self.process])]

    def process(self, body, message):
        """Handle incoming message.

        We hand off processing to the worker callback, and manage calling the
        retry policy or ack()ing the message depending on the returned value
        from the worker.

        """
        try:
            requested_action = self.on_message_cb(body)
            if requested_action == MessageActions.Retry:
                # delegate to the retry policy:
                self.retry_policy.retry(self.connection, message)
            elif requested_action == MessageActions.Acknowledge:
                message.ack()
            elif requested_action is None:
                # treat this as a silent ack, but maybe we should change this
                # to print a warning in the future?
                message.ack()
        # Make it possible to use a debugger inside the worker callback:
        except bdb.BdbQuit:
            raise
        except Exception as e:
            logger.error(
                "Caught unhandled exception while processing message: %s",
                e,
            )
            self.retry_policy.retry(self.connection, message)


class RetryPolicy(object):

    """Encapsulate a retry policy.

    This is a base class for all retry policies. A retry policy dictates what
    happens to a message when the consumer callback returns
    MessageActions.Retry.

    The work is done in the 'retry' method. The policy can do anything it
    likes with the message, including:

    * ack()ing the message and putting a new message on another queue.
    * reject()ing or requeue()ing the message,
    * ...or anythingg else.

    The only requirement is that the policy *must* handle the message given
    to it. No further processing will be done on the message, so one of
    ack() retry() or requeue() must be called.

    """

    def  retry(self, connection, message):
        """Determine what to do with 'message'."""
        pass


class DefaultRetryPolicy(RetryPolicy):

    """A sensible 'N-strikes' retry policy.

    This policy will retry a message a certain number of times by re-inserting
    the message into the last queue it was in. When it's retry limit has been
    exceeded, the message will instead be inserted into a dead-letter queue.

    """

    def __init__(self, max_retries, dead_queue):
        """Create a new DefaultRetryPolicy.

        'max_retries' specifies the number of times a message will be retried.
        'dead_queue' specifies the name of the dead-letter queue to use.

        """
        self.max_retries = max_retries
        self.dead_queue = dead_queue

    def retry(self, connection, message):
        last_queue_name = message.delivery_info['routing_key']
        retry_key = "{}_retry_count".format(last_queue_name)
        retry_count = int(message.payload.get(retry_key, '0'))

        if retry_count < self.max_retries:
            message.payload[retry_key] = retry_count + 1
            queue = connection.SimpleQueue(last_queue_name)
            queue.put(message.payload)
            queue.close()
            message.ack()
        else:
            logger.error(
                "Rejecting message due to retry count exceeding maximum. "
                "Message will reside on the dead letter queue",
            )
            queue = connection.SimpleQueue(self.dead_queue)
            queue.put(message.payload)
            queue.close()
            message.ack()
