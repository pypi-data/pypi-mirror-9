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

"""Integration tests for the kombu queue code."""

import kombu
import kombu.simple
from testtools import TestCase

from testtools.matchers import (
    Contains,
    Equals,
)


from uservice_utils.queue import (
    DefaultRetryPolicy,
    MessageActions,
    SimpleRabbitQueueWorker,
)


class KombuQueueIntegrationTests(TestCase):

    def test_can_read_and_accept_message(self):
        conn = kombu.Connection('memory:///')
        queue_name = self.getUniqueString()
        queue_message(conn, queue_name, {'test': 'value'})
        retry_policy = LoggingRetryPolicy()

        consumer = LoggingConsumer(MessageActions.Acknowledge)
        q = SimpleRabbitQueueWorker(
            conn,
            queue_name,
            consumer,
            retry_policy,
        )
        # pump the queue to get the enqueued message:
        next(q.consume(limit=1, timeout=5.0))

        self.assertEqual(consumer.got_messages, [dict(test='value')])
        self.assertEqual(retry_policy.payloads_retried, [])

    def test_uncaught_exceptions_cause_message_retry(self):
        conn = kombu.Connection('memory:///')
        queue_name = self.getUniqueString()
        message = {'test': 'value'}
        queue_message(conn, queue_name, message)
        retry_policy = LoggingRetryPolicy()

        def consumer_with_bug(message):
            raise RuntimeError("I am a bug, all up in ur bizniz!")
        queue = SimpleRabbitQueueWorker(
            conn,
            queue_name,
            consumer_with_bug,
            retry_policy
        )
        next(queue.consume(limit=1, timeout=5.0))

        self.assertEqual(retry_policy.payloads_retried, [message])

    def test_retry_message_works(self):
        conn = kombu.Connection('memory:///')
        queue_name = self.getUniqueString()
        message = {'test': 'value'}
        queue_message(conn, queue_name, message)
        retry_policy = LoggingRetryPolicy()

        consumer = LoggingConsumer(MessageActions.Retry)
        q = SimpleRabbitQueueWorker(
            conn,
            queue_name,
            consumer,
            retry_policy,
        )
        # pump the queue to get the enqueued message:
        next(q.consume(limit=1, timeout=5.0))

        self.assertEqual(consumer.got_messages, [message])
        self.assertEqual(retry_policy.payloads_retried, [message])


class DefaultRetryPolicyTests(TestCase):
    """Tests for the default retry policy."""

    def route_message(self, connection, queue_name, message):
        """Route a message in an input queue, so we get a proper message object.

        Since we rely on kombu having actually made us a proper message object,
        we take 'message' and put it on the input queue, then retrieve it again.

        """
        q = kombu.simple.SimpleQueue(connection, queue_name)
        q.put(message)
        return q.get(timeout=5.0)

    def test_retry_message(self):
        input_queue, dead_queue = 'input.queue', 'dead.queue'
        conn = kombu.Connection('memory:///')
        message = self.route_message(
            conn,
            input_queue,
            dict(test='value')
        )
        policy = DefaultRetryPolicy(max_retries=1, dead_queue=dead_queue)

        policy.retry(conn, message)

        # make sure the input message was dealt with:
        self.assertTrue(message.acknowledged)

        # look in our input queue and make sure out message is there with a new
        # retry count:
        new_message = conn.SimpleQueue(input_queue).get(timeout=5.0)
        new_payload = new_message.payload

        expected_retry_key = input_queue + '_retry_count'
        self.assertThat(new_payload, Contains(expected_retry_key))
        self.assertThat(new_payload[expected_retry_key], Equals(1))

    def test_kill_message(self):
        input_queue, dead_queue = 'input.queue', 'dead.queue'
        conn = kombu.Connection('memory:///')
        message = self.route_message(
            conn,
            input_queue,
            dict(test='value')
        )
        policy = DefaultRetryPolicy(max_retries=0, dead_queue=dead_queue)

        policy.retry(conn, message)

        # make sure the input message was dealt with:
        self.assertTrue(message.acknowledged)

        # look in the dead letter queue and make sure our message is there
        new_message = conn.SimpleQueue(dead_queue).get(timeout=5.0)
        new_payload = new_message.payload

        # The policy shouldn't alter the payload when moving to the dead letter queue
        self.assertThat(new_payload, Equals(dict(test='value')))


class LoggingConsumer(object):

    """A consumer callback object that acks and logs all received payloads."""

    def __init__(self, return_action):
        self.got_messages = []
        self.return_action = return_action

    def __call__(self, payload):
        self.got_messages.append(payload)
        return self.return_action


class LoggingRetryPolicy(object):

    """A fake retry policy that ack()s all messages, but logs their payloads."""
    def __init__(self):
        self.payloads_retried = []

    def retry(self, connection, message):
        self.payloads_retried.append(message.payload)
        message.ack()


def queue_message(conn, queue, message):
    q = kombu.simple.SimpleQueue(conn, queue)
    q.put(message)
