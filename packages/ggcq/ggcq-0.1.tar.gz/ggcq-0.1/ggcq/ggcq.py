# -*- coding: utf-8 -*-

'''

   Copyright 2015 The pyggcq Developers

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

'''

import logging

import simpy

logger = logging.getLogger(__name__)


class GGCQServiceTimeStopIteration(RuntimeError):
    """
    Exception thrown if service time generator is exhausted

    Should not base StopIteration as simpy uses that exception to signify the
    end of the process!
    """
    pass


class GGCQServiceTimeTypeError(TypeError):
    """
    Exception thrown if service time is of wrong type
    """
    pass


class GGCQArrivalTimeTypeError(TypeError):
    """
    Exception thrown if arrival time is of wrong type
    """
    pass


class GGCQNegativeArrivalTimeError(ValueError):
    """
    Exception thrown if arrival time is negative
    """
    pass


class GGCQNegativeServiceTimeError(ValueError):
    """
    Exception thrown if service time is negative
    """
    pass


class GGCQ(object):

    def __init__(
        self, arrival_time_generator, service_time_generator, capacity=1
    ):
        # initialize logging
        self._logger = logging.getLogger(
            '{}.{}'.format(__name__, self.__class__.__name__)
        )
        self._logger.debug('init')
        self._arrival_time_generator = arrival_time_generator
        self._service_time_generator = service_time_generator
        self._capacity = capacity
        self._env = simpy.Environment()
        self._observer = RawDataObserver()
        self._queue = Queue(
            env=self._env,
            service_time_generator=service_time_generator,
            observer=self._observer,
            capacity=capacity,
        )
        self._source = Source(
            env=self._env,
            queue=self._queue,
            arrival_time_generator=arrival_time_generator,
            observer=self._observer,
        )

        # start arrival process
        self._logger.info('start arrival process')
        self._env.process(self._source.generate())

    def run(self, until=None):
        self._env.run(until=until)

    @property
    def now(self):
        return self._env.now


class RawDataObserver(object):

    JOB_COLUMNS = ['arrival_epoch', 'service_epoch', 'departure_epoch']

    def __init__(self):
        self._jobs = dict()

    def notify_arrival(self, time, job_id):
        self._jobs[job_id] = [time] + 2 * [None]

    def notify_service(self, time, job_id):
        self._jobs[job_id][1] = time

    def notify_departure(self, time, job_id):
        self._jobs[job_id][2] = time

    @property
    def jobs(self):
        return self._jobs


class Queue(object):

    def __init__(self, env, service_time_generator, observer, capacity=1):
        # initialize logging
        self._logger = logging.getLogger(
            '{}.{}'.format(__name__, self.__class__.__name__)
        )
        self._logger.debug('init')
        self._env = env
        self._capacity = capacity
        self._queue = simpy.Resource(env, capacity=self._capacity)
        self._service_time_generator = service_time_generator
        self._observer = observer

    def process(self, job_id):
        """
        Process a job by the queue
        """

        self._logger.info(
            '{:.2f}: Process job {}'.format(self._env.now, job_id)
        )

        # log time of commencement of service
        self._observer.notify_service(time=self._env.now, job_id=job_id)

        # draw a new service time
        try:
            service_time = next(self._service_time_generator)
        except StopIteration:
            # ERROR: no more service times
            error_msg = ('Service time generator exhausted')
            self._logger.error(error_msg)

            # raise a different exception, as simpy uses StopIteration to
            # signify end of process (generator)
            raise GGCQServiceTimeStopIteration(error_msg)

        # wait for the service time to pass
        try:
            self._logger.debug('Service time: {:.2f}'.format(service_time))
        except:
            pass

        try:
            yield self._env.timeout(service_time)

        except TypeError:
            # error: service time of wrong type
            error_msg = (
                "service time '{}' has wrong type '{}'".format(
                    service_time, type(service_time).__name__
                )
            )
            self._logger.error(error_msg)

            # trigger exception
            raise GGCQServiceTimeTypeError(error_msg)

        except ValueError as exc:
            if str(exc).startswith('Negative delay'):
                # error: negative service time
                error_msg = (
                    "negative service time {:.2f}".format(
                        service_time
                    )
                )
                self._logger.error(error_msg)

                # trigger exception
                raise GGCQNegativeServiceTimeError(error_msg)
            else:
                raise

        # job finished processing -> departing
        self._logger.info(
            '{:.2f}: Finished processing job {}'.format(self._env.now, job_id)
        )
        # log departure epoch
        self._observer.notify_departure(time=self._env.now, job_id=job_id)

    @property
    def queue(self):
        return self._queue


class Source(object):

    def __init__(self, env, queue, arrival_time_generator, observer):
        # initialize logging
        self._logger = logging.getLogger(
            '{}.{}'.format(__name__, self.__class__.__name__)
        )
        self._logger.debug('init')
        self._env = env
        self._queue = queue
        self._arrival_time_generator = arrival_time_generator
        self._job_id = 0
        self._observer = observer

    def generate(self):
        """
        Source generates jobs according to the interarrival time distribution
        """
        inter_arrival_time = 0.0
        while True:
            # wait for next job to arrive
            try:
                yield self._env.timeout(inter_arrival_time)

            except TypeError:
                # error: arrival time of wrong type
                error_msg = (
                    "arrival time '{}' has wrong type '{}'".format(
                        inter_arrival_time, type(inter_arrival_time).__name__
                    )
                )
                self._logger.error(error_msg)

                # trigger exception
                raise GGCQArrivalTimeTypeError(error_msg)

            except ValueError as exc:
                if str(exc).startswith('Negative delay'):
                    # error: negative arrival time
                    error_msg = (
                        "negative arrival time {:.2f}".format(
                            inter_arrival_time
                        )
                    )
                    self._logger.error(error_msg)

                    # trigger exception
                    raise GGCQNegativeArrivalTimeError(error_msg)
                else:
                    raise

            # job has arrived
            job_id = self._job_id
            self._observer.notify_arrival(time=self._env.now, job_id=job_id)

            # get job process
            job = self._job_generator(job_id)

            # submit job to queue
            self._env.process(job)

            # time for the next job to arrive
            try:
                inter_arrival_time = next(self._arrival_time_generator)
                self._job_id += 1
            except StopIteration:
                # no more jobs to arrive -- exit process
                self._env.exit()

    def _job_generator(self, job_id):
        with self._queue.queue.request() as request:
            # wait for queue to become idle
            yield request
            # process job
            yield self._env.process(self._queue.process(job_id))
