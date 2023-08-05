from gevent import monkey; monkey.patch_all()
from kafka import KafkaClient, SimpleProducer, SimpleConsumer

import logging
logging.basicConfig(level=logging.INFO)

# To send messages synchronously
kafka = KafkaClient("localhost:9092")

producer = SimpleProducer(kafka)


# To consume messages
consumer = SimpleConsumer(kafka, "my-group", "my-topic")
consumer.provide_partition_info()
#consumer.seek(0, 0)
print consumer.pending()
for partition, message in consumer:
    # message is raw byte string -- decode if necessary!
    # e.g., for unicode: `message.decode('utf-8')`
    print 'p{0}'.format(partition), (message.offset, message.message.__dict__)

kafka.close()