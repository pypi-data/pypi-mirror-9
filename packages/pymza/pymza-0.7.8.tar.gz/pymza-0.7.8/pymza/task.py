import time
import logging
import types
import gevent
import json
import ujson
from gevent.queue import Queue, Empty

import kafka.common
from kafka import SimpleConsumer, KeyedProducer
from kafka.conn import DEFAULT_SOCKET_TIMEOUT_SECONDS


from .utils import ExponentialSleep, IntervalTracker
from .const import FETCH_BUFFER_SIZE_BYTES, MAX_FETCH_BUFFER_SIZE_BYTES, GET_MESSAGE_TIMEOUT
from .message import SourceMessage
from .kafka_utils import get_kafka_offset_range


class Task(object):
    def __init__(self, name, code):
        self.name = name
        self.code = code

    @property
    def description(self):
        return self.code.__doc__

    @property
    def source_topics(self):
        return self.code.SOURCE_TOPICS

    @property
    def result_topics(self):
        return getattr(self.code, 'RESULT_TOPICS', [])

    @property
    def is_windowed(self):
        return bool(self.window_interval)

    @property
    def window_interval(self):
        val = getattr(self.code, 'WINDOW_INTERVAL', None)
        if val is not None:
            return float(val)

    def init(self, config):
        if not hasattr(self.code, 'init'):
            return
        return self.code.init(config)

    def process(self, message, state):
        return self.code.process(message, state)

    def window(self, state):
        return self.code.window(state)


class TaskInstance(object):

    def __init__(self, kafka, task, partition_id, state_mgr, config):
        self.kafka = kafka
        self.task = task
        self.partition_id = partition_id
        self.producer = KeyedProducer(self.kafka)
        self.state_mgr = state_mgr
        self.last_window_time = time.time()
        self.logger = logging.getLogger('pymza.task.{0}'.format(self.name))
        self.queue = Queue(maxsize=1000)
        self.last_commit = time.time()
        self.config = config

        self.state = self.state_mgr.state

        commit_interval = 5*60
        try:
            commit_interval = int(config.get('commit_interval'))
        except (TypeError, ValueError):
            pass
        self.commit_time = IntervalTracker(commit_interval)

        window_interval = self.task.window_interval
        try:
            window_interval = int(config.get('window_interval'))
        except (TypeError, ValueError):
            pass

        self.result_topics = set(self.task.result_topics)

        self.offsets = self.state_mgr.offsets
        if self.task.is_windowed:
            self.window_time = IntervalTracker(window_interval)
        else:
            self.window_time = None

    @property
    def name(self):
        return self.task.name

    def __repr__(self):
        return 'TaskInstance({0}, {1})'.format(self.name, self.partition_id)

    def run(self):
        self.logger.debug('Starting...')

        self.task.init(self.config)

        consumers = []
        for topic in self.task.source_topics:
            consumer = SimpleConsumer(self.kafka,
                                      self.name, topic, 
                                      partitions=[self.partition_id],
                                      auto_commit=False,
                                      buffer_size=FETCH_BUFFER_SIZE_BYTES,
                                      max_buffer_size=MAX_FETCH_BUFFER_SIZE_BYTES)

            server_offsets = get_kafka_offset_range(self.kafka, [(topic, self.partition_id)])
            for topic, partition_id, server_min, server_max in server_offsets:
                our_offset = self.offsets.get(topic)
                if our_offset > server_max:
                    raise RuntimeError('Stored offset for topic {0} and partition {1} ({2}) is larger '
                        'than maximal offset on server ({3}). This could be caused by state not synchronized '
                        'with data in Kafka. You are adviced to wipe state and reprocess all data in Kafka.'.format(topic, partition_id, our_offset, server_max))
                elif our_offset < server_min:
                    self.logger.warn('Our offset for topic {0} and partition {1} ({2}) is smaller than'
                    ' minimal offset on server ({3}). This could be caused by log compaction. Updating '
                    'our offset to server minimal offset.'.format(topic, partition_id, our_offset, server_min))
                    self.offsets.force_set(topic, server_min)

            # set consumer offsets to stored ones
            consumer.offsets[self.partition_id] = self.offsets.get(topic)
            consumer.fetch_offsets = consumer.offsets.copy()

            consumers.append(consumer)

        # spawn consumer threads
        for consumer in consumers:
            gevent.spawn(_reader_thread, self, consumer, self.queue)


        while True:
            try:
                task, consumer, partition, message_envelope = self.queue.get(block=True, timeout=1)
            except Empty:
                self.maybe_window()
                self.maybe_commit()
                continue

            message = SourceMessage(json.loads(message_envelope.message.value), source=consumer.topic, key=message_envelope.message.key)
            result = self.task.process(message, self.state)
            self.handle_task_result(result)

            self.offsets.set(consumer.topic, message_envelope.offset+1)

            # for windowed tasks offsets commited only when `window` called
            if not self.task.is_windowed:
                self.offsets.apply_new_offsets()

            self.maybe_commit()

            gevent.sleep(0)  # to give chance for other greenlets to run

    def maybe_window(self):
        if self.window_time:
            result = self.task.window(self.state)
            self.handle_task_result(result)

            self.window_time.reset()
            self.offsets.apply_new_offsets()

    def maybe_commit(self):
        if self.commit_time:
            self.commit()

            self.commit_time.reset()

    def commit(self):
        # commit state
        if self.state.is_modified:
            self.logger.debug('Commiting state...')
            try:        
                self.state.commit()
            except Exception:
                self.logger.exception('Failed to serialize state for task {0}'.format(self.name))
                raise

        # commit offsets
        if self.offsets.is_modified:
            self.logger.debug('Commiting offsets...')
            self.state_mgr.commit_offsets()


    def handle_task_result(self, results):
        if results is None:
            results = []

        try:
            for result in results:
                if result is None:
                    continue
                topic, key, value = result
                if topic not in self.result_topics:
                    self.logger.error('Task yielded data into {0} but task result topics defined as {1}. Message not sent.'.format(topic, list(self.result_topics)))
                    raise
                if key is None:
                    self.logger.error('Task yielded data with no key. Message not sent.')
                try:                    
                    self.producer.send(ensure_str(topic), ensure_str(key), ujson.dumps(value))
                except Exception:
                    self.logger.exception('Failed to send message to {0}:{1}'.format(topic, key))
                    raise
        except Exception:
            self.logger.exception('Failed to process result of {0}'.format(self.name))
            raise

def _reader_thread(task, consumer, queue):
    sleep = ExponentialSleep(0.1, 10, 2.0)
    while True:
        try:
            while True:
                result = consumer.get_message(
                    block=True, timeout=GET_MESSAGE_TIMEOUT, get_partition_info=True)
                if result is None:
                    continue
                partition, message = result
                queue.put((task, consumer, partition, message))
                sleep.reset()
        except Exception:
            if sleep.current > 0.5:
                task.logger.exception('Error while reading messages for {0}/{1}. Sleeping for {2}.'.format(
                    task.name, consumer.topic, sleep.current))
            sleep.sleep()


def ensure_str(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return str(s)