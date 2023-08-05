# encoding: utf-8

import json
import logging
import time
import threading

from docker import Client

from .RWLock import RWLock

__all__ = [
    'ContainerStatsEmitter',
    'ContainerStats'
]

class ContainerStats(threading.Thread):
    """Provides a set of metrics about a Docker container.

    Those metrics are updated repeatedly (about every second) by
    `stats` method available in Docker remote API since v17.

    TODO: make it a thread
    """

    def __init__(self, container, docker):
        """
        :param container: The Docker container identifier to monitor.

        :param docker: Docker client
        :type docker: Client
        """
        threading.Thread.__init__(self)
        self.container = container
        self.name = docker.inspect_container(container)['Name'][1:]
        self.cpu_percent = 0.0
        self.memory = 0.0
        self.memory_limit = 0.0
        self.memory_percent = 0.0
        self.network_rx = 0.0
        self.network_tx = 0.0
        self.stats = None
        self.timestamp = int(time.time())
        self._docker = docker
        self._lock = RWLock()
        self._response = None

    def run(self):
        """Collect container metrics repeatedly. Does not returns
        unless the Docker stats stream is closed or the `shutdown` method
        is called.
        """
        previous_cpu = 0.0
        previous_system = 0.0
        start = True
        url = self._docker._url("/containers/{0}/stats".format(self.container))
        self._response = self._docker._get(url, stream=True)
        stream = self._docker._stream_helper(self._response, decode=True)
        try:
            for stats in stream:
                # strongly inspired from docker's code.
                mem_percent = float(stats['memory_stats']['usage']) / stats['memory_stats']['limit'] * 100.0
                cpu_percent = 0.0
                if not start:
                    cpu_percent = self._calculate_cpu_percent(previous_cpu, previous_system, stats)
                start = False
                self._lock.acquire_write()
                self.timestamp = int(time.time())
                self.stats = stats
                self.cpu_percent = cpu_percent
                self.memory = float(stats['memory_stats']['usage'])
                self.memory_limit = float(stats['memory_stats']['limit'])
                self.memory_percent = mem_percent
                self.network_rx = float(stats['network']['rx_bytes'])
                self.network_tx = float(stats['network']['tx_bytes'])
                self._lock.release()
                previous_cpu = stats['cpu_stats']['cpu_usage']['total_usage']
                previous_system = stats['cpu_stats']['system_cpu_usage']
        except AttributeError:
            # raise in urllib3 when the stream is closed while waiting for stuff to read
            pass
        finally:
            self.shutdown() # ensure stream is closed

    def emit(self, consumer_func):
        """Provide consumer access to the container stats.

        :param: `consumer_func`: callable instance. This parameter is called with
        this instance given in parameter.

        TODO: pass a dict() of values directly.
        """
        self._lock.acquire_read()
        try:
            consumer_func(self)
        finally:
            self._lock.release()


    def shutdown(self):
        """Stop collecting the container metrics.
        """
        if self._response:
            self._response.raw.close()
            self._response = None

    def _calculate_cpu_percent(self, previous_cpu, previous_system, stats):
        """Compute CPU percentage.

        strongly inspired from docker's code.

        :return: cpu percentage
        """
        cpu_percent = 0.0
        # calculate the change for the cpu usage of the container in between readings
        cpu_delta = float(stats['cpu_stats']['cpu_usage']['total_usage']) - previous_cpu
        # calculate the change for the entire system between readings
        system_delta = float(stats['cpu_stats']['system_cpu_usage']) - previous_system
        if system_delta > 0.0 and cpu_delta > 0.0:
            cpu_percent = (cpu_delta / system_delta) * float(len(stats['cpu_stats']['cpu_usage']['percpu_usage'])) * 100.0
        return cpu_percent


class ContainerStatsEmitter(threading.Thread):
    """Maintain a list of `ContainerStats` collecting metrics of several Docker containers.
    Repeatedly aggregates all metrics and push them to a consumer. The list of container collectors
    is updated according to containers started, stopped, ...
    """

    def __init__(self, client, endpoint_func, delay=30):
        """
        :param client: Docker client

        :param endpoint_func: a callable instance which is given aggregated statistics repeadetly.

        :param delay: Number of seconds between 2 notifications of `endpoint_func`
        """
        threading.Thread.__init__(self)
        self._client = client
        self._endpoint_func = endpoint_func
        self._delay = delay
        self._stop = False
        self._logger = logging.getLogger("stats-emitter")

    def run(self):
        container_stats = dict()
        try:
            while self._should_run():
                # update list of container stats
                running_containers = set(map(lambda c: c['Id'], self._client.containers()))
                monitored_containers = set(container_stats.keys())
                started_containers = running_containers - monitored_containers
                stopped_containers = monitored_containers - running_containers
                for container in stopped_containers:
                    self._logger.info("container has stopped: %s", container)
                    container_stats.pop(container).shutdown()
                for container in started_containers:
                    self._logger.info("container has started: %s", container)
                    stats = ContainerStats(container, self._client)
                    container_stats[container] = stats
                    stats.start()
                time.sleep(self._delay)
                # collect results
                payload = []
                def append(stats):
                    payload.append({
                        'name': stats.name,
                        'id': stats.container,
                        'stats': stats.stats,
                        'cpu_percent': stats.cpu_percent,
                        'memory': stats.memory,
                        'memory_limit': stats.memory_limit,
                        'memory_percent': stats.memory_percent,
                        'network_rx': stats.network_rx,
                        'network_tx': stats.network_tx,
                        'timestamp': stats.timestamp,
                    })
                for stats in container_stats.values():
                    stats.emit(append)
                # emit to endpoint_func
                self._endpoint_func(self._client, payload)
        finally:
            self._logger.info("waiting for all collectors threads to terminate.")
            for container in container_stats.values():
                container.shutdown()
            for container in container_stats.values():
                container.join()
            self._logger.info("collectors terminated successfully. See you bye!")

    def shutdown(self):
        """Ask thread termination. Method returns immediatly. You may
        call the `Thread.join` method afterward."""
        self._logger.info("user asked for daemon termination.")
        self._stop = True

    def _should_run(self):
        """Internal method used to know if the show must go on"""
        return not self._stop
