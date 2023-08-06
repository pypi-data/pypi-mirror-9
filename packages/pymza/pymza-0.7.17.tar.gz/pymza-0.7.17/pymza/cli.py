import gevent
from gevent import monkey
monkey.patch_all()
import logging
import click
import sys
import signal
import os.path
import gevent

from .config import Config

pass_config = click.make_pass_decorator(Config, ensure=False)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--config', required=True, help='config file', type=click.Path(file_okay=True, dir_okay=False, exists=True), multiple=True)
@click.option('-l', '--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARN', 'ERROR']))
@click.pass_context
def main(ctx, config, log_level):
    ctx.obj = Config(config)

    ctx.obj.add_home_to_pythonpath()

    log_level = getattr(logging, log_level)
    logging.basicConfig(level=log_level)
    logging.getLogger('kafka').setLevel(logging.WARN)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARN)


@main.command()
@pass_config
@click.option('-n', '--num-processes', type=int, default=1, help="Total number of processes that you want to launch.")
@click.option('-c', '--this-process', type=int, default=1, help="Number of this process (must be between 1 and num-processes).")
@click.option('-s', '--report-stats', is_flag=True, help="Should we report stats to pymza_stats topic?")
def run(config, this_process, num_processes, report_stats):
    """Start stream processing with configuration specified in config file"""
    click.echo("running")

    from .container import TaskContainer, InstanceChooser
    from .state import StateManager
    from .reporting import container_reporter

    state_manager = StateManager(config.state_dir())
    tasks = [config.load_task(x) for x in config.tasks()]

    chooser = InstanceChooser(this_process-1, num_processes)

    c = TaskContainer(config.kafka_hosts, tasks, state_manager, config, chooser)

    def print_stats(signum, frame):
        print "Current stats:"
        gevent.spawn(c.print_stats)
    signal.signal(signal.SIGUSR1, print_stats)

    greenlets = [gevent.spawn(c.run)]
    if report_stats:
        greenlets.append(gevent.spawn(container_reporter, c, c.kafka))

    gevent.joinall(greenlets, raise_error=True)


@main.command()
@pass_config
@click.argument('dotfile', required=True, type=click.Path(file_okay=True, dir_okay=False))
def topology(config, dotfile):
    click.echo("Saving topology to {0}".format(dotfile))

    with open(dotfile, 'w') as f:
        topics = set()

        print >>f, "digraph topology {"
        for task in [config.load_task(x) for x in config.tasks()]:
            print >>f, "task_{0} [label=\"{0}\", tooltip=\"{1}\", shape=box, style=bold]".format(
                task.name, task.description)

            for s in task.source_topics:
                if s not in topics:
                    topics.add(s)
                print >>f, "topic_{0} -> task_{1}".format(s, task.name)
            for s in task.result_topics:
                if s not in topics:
                    topics.add(s)
                print >>f, "task_{0} -> topic_{1}".format(task.name, s)

        for topic in topics:
            print >>f, "topic_{0} [label=\"{0}\", tooltip=\"{1}\", shape=ellipse, style=dashed]".format(
                topic, getattr(topic, '__doc__', topic + ' topic'))

        print >>f, "}"

    click.echo(
        "Done. You can run `dot {0}  -Tsvg -o {1}.svg` to convert it to SVG.".format(dotfile, os.path.splitext(dotfile)[0]))


@main.command()
@pass_config
@click.option('--zookeeper', default='127.0.0.1')
@click.option('--partitions', default=1)
@click.option('--replication-factor', default=1)
def create_topics(config, zookeeper, partitions, replication_factor):
    topics = set()

    for task in [config.load_task(x) for x in config.tasks()]:
        topics.update(task.source_topics)
        topics.update(task.result_topics)

    print >>sys.stderr, "Please run following commands to create topics:"
    for topic in sorted(topics):
        print "./bin/kafka-topics.sh --zookeeper {zookeeper} --create --topic {topic} --replication-factor {replication_factor} --partitions {partitions}".format(**locals())


@main.command()
@click.argument('task_name')
def reset(task_name):
    click.echo("Resetting {0}".format(task_name))

    # stopping
    # resetting state
    # seeking to 0
    # starting


@main.command()
@pass_config
def topics(config):
    topics = set()

    for task in [config.load_task(x) for x in config.tasks()]:
        topics.update(task.source_topics)
        topics.update(task.result_topics)

    for t in sorted(topics):
        print t


@main.command()
@pass_config
@click.argument('task')
def offsets(config, task):

    task = config.load_task(task)
    from .state import StateManager
    state_manager = StateManager(config.state_dir())
    ostore = state_manager.get_offset_store(task)

    from pymza.offset import SimpleOffsetTracker

    offset = SimpleOffsetTracker()
    ostore.load(offset)

    print offset._offsets


@main.command()
@click.option('--kafka', default="localhost:9092")
@click.option('--from-start', 'seek', flag_value='start',
              default=False)
@click.option('--from-end', 'seek', flag_value='end',
              default=True)
@click.argument('topic')
def topic_tail(kafka, topic, seek):
    from kafka import KafkaClient, SimpleConsumer

    kafka = KafkaClient(kafka)

    consumer = SimpleConsumer(
        kafka, "my-group", str(topic), auto_commit=False, max_buffer_size=10 * 1024 * 1024)
    consumer.provide_partition_info()

    if seek == 'start':
        consumer.seek(0, 0)
    elif seek == 'end':
        print "Seeking to end"
        consumer.seek(2, 0)
    click.echo(
        "Tailing {0}, {1} messages pending".format(topic, consumer.pending()))
    for partition, message in consumer:
        print 'k:', message.message.key
        print 'v:', message.message.value
        print

    kafka.close()

if __name__ == '__main__':
    main()
