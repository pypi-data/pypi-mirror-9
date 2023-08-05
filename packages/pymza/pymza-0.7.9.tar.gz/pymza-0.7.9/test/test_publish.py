from gevent import monkey; monkey.patch_all()
import json
from kafka import KafkaClient, SimpleProducer, SimpleConsumer
from kafka import KafkaClient, KeyedProducer, HashedPartitioner, RoundRobinPartitioner

import logging
logging.basicConfig(level=logging.DEBUG)


# To send messages synchronously
kafka = KafkaClient("localhost:9092")

#print kafka.get_partition_ids_for_topic('my-topic')
#print kafka.load_metadata_for_topics('my-topic')

#producer = SimpleProducer(kafka)

#response = producer.send_messages("my-topic", "another message")


producer = KeyedProducer(kafka)
# producer.send("my-topic", "key1", "some message")
# producer.send("my-topic", "key2", "this methode")

data = [
    ('423469835234734081', 'http://t.co/4S2IzfcZIO'),
    ('212917600320098304', 'http://t.co/C74SuTJC'),
    ('423104608915845120', 'http://t.co/4S2IzfcZIO'),
    ('422711045459673088', 'http://t.co/4S2IzfcZIO'),
    ('422657598488186881', 'http://t.co/4S2IzfcZIO'),
]

#for i in range(10):
for tweet_id, url in data:
    producer.send('tweet_urls', tweet_id, json.dumps(dict(tweet_id=tweet_id, url=url)))

producer.stop(timeout=10)
kafka.close()
import time
time.sleep(0.5)