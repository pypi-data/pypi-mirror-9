import time
import json
from kafka import KeyedProducer
from kafka_utils import get_kafka_offset_range


def container_reporter(container, kafka, reporting_interval=5):

    producer = KeyedProducer(kafka)

    used_topic_partitions = {
        (topic, partition_id)
        for task, instance_dict in container.task_instances.iteritems()
        for partition_id in instance_dict
        for topic in task.source_topics
    }

    while True:
        time.sleep(reporting_interval)

        server_offsets = get_kafka_offset_range(kafka, list(used_topic_partitions))
        topic_partition_max_offset = {(topic, partition_id): server_max for topic, partition_id, server_min, server_max in server_offsets}
        topic_partition_min_offset = {(topic, partition_id): server_min for topic, partition_id, server_min, server_max in server_offsets}

        container_stats = {}
        for task, instance_dict in container.task_instances.iteritems():
            for partition_id, instance in instance_dict.iteritems():
                for topic in task.source_topics:
                    instance_stats = container_stats.setdefault(task.name, {}).setdefault(str(partition_id), {})
                    key = (topic, partition_id)
                    min_offs = topic_partition_min_offset[key]
                    max_offs = topic_partition_max_offset[key]
                    cur_offs = instance.get_offset_for_topic(topic)
                    instance_stats[topic] = [cur_offs - min_offs, max_offs-min_offs]

        producer.send('pymza_stats', 'stats', json.dumps(container_stats))