from multiprocessing import Process
from setproctitle import setproctitle
import time
from motorway.controller import ControllerIntersection
from motorway.discovery.local import LocalDiscovery
from motorway.utils import ramp_result_stream_name
import zmq
import logging
from motorway.webserver import WebserverIntersection

logger = logging.getLogger(__name__)


class Pipeline(object):
    def __init__(self, discovery_backend=LocalDiscovery, controller_bind_address="0.0.0.0:7007"):
        self._streams = {}
        self._stream_consumers = {}
        self._processes = []
        self._queue_processes = []
        self._ramp_result_streams = []
        self._discovery_backend = discovery_backend()
        self.controller_bind_address = "tcp://%s" % controller_bind_address
        self.context = zmq.Context()

    def definition(self):
        """
        Extend this method in your :class:`motorway.pipeline.Pipeline` subclass, e.g.::

            class WordCountPipeline(Pipeline):
                def definition(self):
                    self.add_ramp(WordRamp, 'sentence')
                    self.add_intersection(SentenceSplitIntersection, 'sentence', 'word', processes=2)
                    self.add_intersection(WordCountIntersection, 'word', 'word_count', grouper_cls=HashRingGrouper, processes=2)
                    self.add_intersection(AggregateIntersection, 'word_count', grouper_cls=HashRingGrouper, processes=1)
        """
        raise NotImplementedError("You must implement a definition() on your pipeline")

    def _add_process(self, cls, process_instances, process_args, input_stream=None, output_stream=None, show_in_ui=True, process_start_number=0):
        for i in range(process_start_number, process_instances + process_start_number):
            process_name = "%s-%s" % (cls.__name__, i)
            p = Process(
                target=cls.run,
                args=process_args,
                name=process_name
            )
            self._processes.append(p)
            if show_in_ui:
                if output_stream:
                    if output_stream not in self._stream_consumers:
                        self._stream_consumers[output_stream] = {'producers': [], 'consumers': []}
                    self._stream_consumers[output_stream]['producers'].append(process_name)
                if input_stream not in self._stream_consumers:
                    self._stream_consumers[input_stream] = {'producers': [], 'consumers': []}
                self._stream_consumers[input_stream]['consumers'].append(process_name)

    def add_ramp(self, ramp_class, output_stream, processes=1):
        ramp_result_stream = ramp_result_stream_name(ramp_class.__name__)
        self._ramp_result_streams.append((ramp_class.__name__, ramp_result_stream))
        self._add_process(
            ramp_class,
            processes,
            process_args=(
                output_stream,
                self.controller_bind_address
            ),
            output_stream=output_stream,

        )

    def add_intersection(self, intersection_class, input_stream, output_stream=None, processes=1, grouper_cls=None):
        self._add_process(
            intersection_class,
            processes,
            process_args=(
                input_stream,
                output_stream,
                self.controller_bind_address,
                grouper_cls
            ),
            input_stream=input_stream,
            output_stream=output_stream,
        )

    def _add_controller(self):
        self._add_process(
            ControllerIntersection,
            1,
            process_args=(
                self.controller_bind_address,
                self._stream_consumers,
            ),
            process_start_number=1
        )

    def run(self):
        """
        Execute the entire pipeline in several sub processes.

        """

        logger.info("Starting Pipeline!")

        setproctitle("data-pipeline: main")

        # User jobs
        self.definition()
        logger.debug("Loaded definition")

        # Controller Transformer
        # self._add_controller()
        self.add_intersection(ControllerIntersection, None, '_web_server')
        self.add_intersection(WebserverIntersection, '_web_server')

        logger.debug("Running queues")
        for queue_process in self._queue_processes:
            queue_process.start()
        logger.debug("Running pipeline")
        for process in self._processes:
            process.start()

        self._processes += self._queue_processes  # Monitor queue processes and shut then down with the rest
        try:
            while True:
                for process in self._processes:
                    assert process.is_alive()
                time.sleep(0.5)
        except Exception:
            raise
        finally:
            self.kill()
        logger.debug("Finished Pipeline!")

    def kill(self):
        for process in self._processes:
            logger.warn("Terminating %s" % process)
            if process.is_alive():
                process.terminate()
