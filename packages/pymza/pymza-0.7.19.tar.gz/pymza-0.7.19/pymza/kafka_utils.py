import kafka.common

def get_kafka_offset_range(client, topic_partition_pairs):
    # fetch offset range for each partition
    result = []
    reqs = [kafka.common.OffsetRequest(topic, partition_id, -1, 10000) for topic, partition_id in topic_partition_pairs]
    resps = client.send_offset_request(reqs) 
    for resp in resps:
        kafka.common.check_error(resp)
        server_max = resp.offsets[0]
        server_min = resp.offsets[-1]

        result.append((resp.topic, resp.partition, server_min, server_max))
    return result
