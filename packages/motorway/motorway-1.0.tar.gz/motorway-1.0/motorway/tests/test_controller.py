from unittest import TestCase
import datetime
import uuid
import zmq
from motorway.controller import ControllerIntersection
from motorway.messages import Message
from motorway.tests.sample_pipeline import SampleWordCountPipeline
from motorway.tests.utils import override_process_name, ZMQSockMock
from freezegun import freeze_time


class ControllerTestCase(TestCase):

    # Utilities to test the controller

    def setUp(self):
        ctx = zmq.Context()
        self.controller = ControllerIntersection({}, ctx, "ipc://controller_test_case", web_server=False)
        self.control_messages = []
        self.controller_sock = ZMQSockMock(self.control_messages)

    def get_control_messages(self):
        messages = [Message.from_message(self.control_messages.pop(0), self.controller_sock) for msg in self.control_messages]
        return messages

    def run_controller_process_method(self):
        return list(
            self.controller.process(self.get_control_messages())
        )  # Remember list(), to evaluate a generator

    # Tests

    def test_histogram_success(self):
        ramp_uuid = str(uuid.uuid4())
        intersection_uuid = str(uuid.uuid4())
        with freeze_time("2014-01-10 12:00:01"):
            msg_in_ramp = Message(1337, "split this string please", producer_uuid=ramp_uuid)
            msg_in_ramp.send_control_message(self.controller_sock, datetime.timedelta(seconds=2), process_name=ramp_uuid, destination_uuid=intersection_uuid)
            self.run_controller_process_method()
            self.controller.update()
            msg_in_intersection = Message.from_message(msg_in_ramp._message(), self.controller_sock)
            msg_in_intersection.ack()
            self.run_controller_process_method()
            self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['histogram'][0]['success_count'], 1)
        with freeze_time("2014-01-10 12:59:01"):
            self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['histogram'][0]['success_count'], 0)

    def test_histogram_error(self):
        ramp_uuid = str(uuid.uuid4())
        intersection_uuid = str(uuid.uuid4())
        with freeze_time("2014-01-10 12:00:01"):
            msg_in_ramp = Message(1337, "split this string please", producer_uuid=ramp_uuid)
            msg_in_ramp.send_control_message(self.controller_sock, datetime.timedelta(seconds=2), process_name=ramp_uuid, destination_uuid=intersection_uuid)
            self.run_controller_process_method()
            self.controller.update()
            msg_in_intersection = Message.from_message(msg_in_ramp._message(), self.controller_sock)
            msg_in_intersection.fail("some error message", False)
            self.run_controller_process_method()
            self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['histogram'][0]['error_count'], 1)
        with freeze_time("2014-01-10 12:59:01"):
            self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['histogram'][0]['error_count'], 0)

    def test_frequency(self):
        ramp_uuid = str(uuid.uuid4())
        intersection_uuid = str(uuid.uuid4())
        msg = Message(1337, "split this string please", producer_uuid=ramp_uuid)
        msg.send_control_message(self.controller_sock, datetime.timedelta(seconds=2), process_name=ramp_uuid, destination_uuid=intersection_uuid)
        self.run_controller_process_method()
        self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['frequency'][2], 1)

    def test_waiting(self):
        ramp_uuid = str(uuid.uuid4())
        intersection_uuid = str(uuid.uuid4())
        msg_in_ramp = Message(1337, "split this string please", producer_uuid=ramp_uuid)
        msg_in_ramp.send_control_message(self.controller_sock, datetime.timedelta(seconds=2), process_name=ramp_uuid, destination_uuid=intersection_uuid)
        self.run_controller_process_method()
        self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['waiting'], 0)
        self.assertEqual(self.controller.process_statistics[intersection_uuid]['waiting'], 1)
        msg_in_intersection = Message.from_message(msg_in_ramp._message(), self.controller_sock, process_name=intersection_uuid)
        msg_in_intersection.ack()
        self.run_controller_process_method()
        self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['waiting'], 0)
        self.assertEqual(self.controller.process_statistics[intersection_uuid]['waiting'], 0)

    def test_message_timeout(self):
        ramp_uuid = str(uuid.uuid4())
        intersection_uuid = str(uuid.uuid4())
        with freeze_time("2014-01-10 12:00:01"):
            msg_in_ramp = Message(1337, "split this string please", producer_uuid=ramp_uuid)
            msg_in_ramp.send_control_message(self.controller_sock, datetime.timedelta(seconds=2), process_name=ramp_uuid, destination_uuid=intersection_uuid)
            self.run_controller_process_method()
            self.controller.update()
        self.assertEqual(self.controller.process_statistics[ramp_uuid]['waiting'], 0)
        self.assertEqual(self.controller.process_statistics[intersection_uuid]['waiting'], 1)
        with freeze_time("2014-01-10 12:59:01"):
            self.controller.update()
            self.assertEqual(self.controller.process_statistics[ramp_uuid]['waiting'], 0)
            self.assertEqual(self.controller.process_statistics[intersection_uuid]['waiting'], 0)
            self.run_controller_process_method()
            self.assertEqual(self.controller.process_statistics[ramp_uuid]['histogram'][59]['timeout_count'], 0)
            self.assertEqual(self.controller.process_statistics[intersection_uuid]['histogram'][59]['timeout_count'], 1)




