import logging
import gevent
import sys
from collections import defaultdict
import kafka.common
from kafka import KafkaClient


from .const import SOCKET_TIMEOUT
from .task import TaskInstance

logger = logging.getLogger('pymza.container')


class InstanceChooser(object):
    def __init__(self, container_id, total_containers):
        self.container_id = container_id
        self.total_containers = total_containers

    def should_run(self, task, partition_id):
        z='{0}{1}'.format(task.name, partition_id)
        return hash(z)%self.total_containers == self.container_id


class TaskContainer(object):

    def __init__(self, kafka_hosts, tasks, state_manager, repo, instance_chooser):
        self.tasks = tasks
        self.state_manager = state_manager
        self.kafka = KafkaClient(kafka_hosts, timeout=SOCKET_TIMEOUT)
        self.repo = repo
        self.instance_chooser = instance_chooser

    def run(self):
        logger.info('Preparing for processing...')
        self.task_instances = defaultdict(dict)

        partitions = None
        for task in self.tasks:
            # ensure that each source topic has same number of partitions
            for topic in task.source_topics:
                try:
                    self.kafka.ensure_topic_exists(topic, 10)
                except kafka.common.UnknownTopicOrPartitionError:
                    raise RuntimeError('Unable to load metadata for topic {0}.'.format(topic))

            topic_partitions = {topic: self.kafka.get_partition_ids_for_topic(
                topic) for topic in task.source_topics}

            if topic_partitions:
                if not all(x == topic_partitions.values()[0] for x in topic_partitions.values()):
                    raise RuntimeError("Failed to initialize task {0}. All source topics must have same number of partitions ({1!r}).".format(task.name, topic_partitions.values()))

                partitions = topic_partitions.values()[0]

            # create task instance for each partition
            for partition_id in partitions:
                if not self.instance_chooser.should_run(task, partition_id):
                    continue
                task_state_manager = self.state_manager.get_task_state_manager(task, partition_id)
                config = self.repo.task_config(task.name)
                instance = TaskInstance(self.kafka,
                                        task,
                                        partition_id,
                                        task_state_manager,
                                        self.repo.serializer,
                                        config,
                                        )
                self.task_instances[task][partition_id] = instance

        logger.info('Starting processing...')
        try:
            # spawn instances and wait till finished
            greenlets = []
            for task, task_instances in self.task_instances.iteritems():
                greenlets.extend([gevent.spawn(t.run) for t in task_instances.values()])

            gevent.joinall(greenlets, raise_error=True)
        finally:
            self.task_instances = defaultdict(dict)

    def print_stats(self):
        topics = {x for task in self.tasks for x in task.source_topics}

        topic_partitions = [(topic, partition_id)
                            for topic in topics for partition_id in self.kafka.get_partition_ids_for_topic(topic)]

        from collections import defaultdict
        from .kafka_utils import get_kafka_offset_range

        server_offsets = defaultdict(dict)
        for topic, partition_id, server_min, server_max in get_kafka_offset_range(self.kafka, topic_partitions):
            server_offsets[topic][partition_id] = server_max

        for task in sorted(self.tasks, key=lambda x: x.name):
            print >>sys.stderr, task.name

            for topic in sorted(task.source_topics):
                server_topic_offsets = server_offsets[topic]

                for partition_id, server_offset in sorted(server_topic_offsets.items()):
                    instance = self.task_instances[task].get(partition_id)
                    if instance is None:
                        continue
                    task_offset = instance.offsets.get(topic)
                    lag = server_offset - task_offset
                    print >>sys.stderr, '\t{0}:{1} {2}/{3} ({4} lag)'.format(topic, partition_id, task_offset, server_offset, lag)
