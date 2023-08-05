from django.conf import settings
from twisted.internet.task import LoopingCall
from twisted.internet import reactor, threads, defer, task

from dateutil.relativedelta import relativedelta

import importlib
import datetime
import time
import random
import sys
import chalk
import json
import pytz
import traceback


from cStringIO import StringIO

from logging import getLogger
logger = getLogger(__name__)

import redis
REDIS = redis.StrictRedis(
                      host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_QUEUE_DB,
                      password=settings.REDIS_PW
                      )

from . import TIEMPO_REGISTRY, RECENT_KEY, RESULT_PREFIX

from .task import Task


INTERVAL = getattr(settings,'TIEMPO_INTERVAL', 5)
THREAD_COUNT = getattr(settings,'TIEMPO_THREADS', 1)
TASK_GROUPS = ['ALL'] + getattr(settings, 'TIEMPO_GROUPS', [])
RESULT_LIFESPAN = getattr(settings,'TIEMPO_RESULT_LIFESPAN_DAYS', 1)


def utc_now():
    return datetime.datetime.now(pytz.utc)

class CaptureStdOut(list):

    def __init__(self, *args, **kwargs):

        self.task = kwargs.pop('task')
        self.start_time = utc_now()

        super(CaptureStdOut, self).__init__(*args, **kwargs)


    def __enter__(self):
        if settings.DEBUG:
            return self
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        if settings.DEBUG:
            return

        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

    def finished(self, timestamp=None):
        if settings.DEBUG:
            return

        self.timestamp = timestamp
        if not timestamp:
            self.timestamp = utc_now()

        task_key = '%s:%s' % (self.task.key, self.task.uid)
        expire_time = int(((self.timestamp + relativedelta(
            days=RESULT_LIFESPAN)) - self.timestamp).total_seconds())

        pipe = REDIS.pipeline()
        pipe.zadd(RECENT_KEY, self.start_time.strftime('%s'), task_key)
        pipe.set(self.task.uid, self.format_output())
        pipe.expire(self.task.uid, expire_time)
        pipe.execute()


    def format_output(self):

        return json.dumps(
            {
                'task': self.task.key,
                'uid': self.task.uid,
                'start_time': self.start_time.isoformat(),
                'end_time': self.timestamp.isoformat(),
                'duration': (self.timestamp - self.start_time).total_seconds(),
                'output': self
            }
        )


def get_task_keys(TASK_GROUPS):
    """
        creates a dictionary containing a mapping every combination of
        cron like keys with the corresponding amount of time
        until the next execution of such a task if it were to be executed
        now.


        ie:

        {'*.*.*': <1 minute from now>,}
        {'*.5.*': <1 minute from now>,}
        {'*.5.11': <24 hours from now>,}

    """

    time_keys = {}

    now = utc_now()

    #first any tasks that want to happen this minute.
    for tg in TASK_GROUPS:

        # every day, every hour, every minute
        expires = now + datetime.timedelta(minutes=1)
        time_keys['*.*.*']=expires

        # every day, every hour, this minute
        expires = now + datetime.timedelta(hours=1)
        time_keys[now.strftime('*.*.%M')]=expires

        # every day, this hour, this minute
        expires = now + datetime.timedelta(days=1)
        time_keys[now.strftime('*.%H.%M')]=expires

        # this day, this hour, this minute
        expires = now + relativedelta(months=1)
        time_keys[now.strftime('%d.%H.%M')]=expires

        # this day, this hour, every minute
        expires = now + datetime.timedelta(minutes=1)
        time_keys[now.strftime('%d.%H.*')]=expires

        # this day, every hour, every minute
        expires = now + datetime.timedelta(minutes=1)
        time_keys[now.strftime('%d.*.*')]=expires

        # every day, this hour, every minute
        expires = now + datetime.timedelta(minutes=1)
        time_keys[now.strftime('*.%H.*')]=expires

    # logger.debug(time_keys.keys())
    return time_keys






class ThreadManager(object):

    def __init__(self, number):
        self.active_task = None
        self.number = number

    def __repr__(self):
        return 'tiempo thread %d'%self.number

    def control(self):
        chalk.blue('%r checking for work'%self)

        """
            First we check our task registry and check if there are any
            tasks that should be running right this second.

            If there are, we queue them.

            Next we execute queued tasks

        """

        now = utc_now()
        tomorrow = now + datetime.timedelta(days=1)

        time_tasks = get_task_keys(TASK_GROUPS)

        for task in [t for t in TIEMPO_REGISTRY.values() if t.group in TASK_GROUPS and t.periodic]:
            stop_key = '%s:schedule:%s:stop'%(task.group,task.key)

            expire_key = time_tasks.get(task.get_schedule())
            # the expire key is a datetime which signifies the NEXT time this task would run
            # if it was to be run right now.
            #
            # if there is no expire key it means that there are no tasks that should run right now.

            if expire_key:
                # if we are here, it means we have a task that could run
                # right now if no other worker has already started it.
                try:

                    # create a key whose existence prevents this task
                    # from executing.  This will ensure that it only runs
                    # once across the whole network.

                    if REDIS.setnx(stop_key, 0):
                        logger.debug('running task %r because: %r', task, task.get_schedule())
                        logger.debug('expire key: %r', expire_key)
                        logger.debug('now: %r', now)
                        logger.debug('stop key: %r', stop_key)
                        logger.debug('seconds: %r', (expire_key-now).total_seconds())
                        # the creation of the key was successful.
                        # this means that previous keys whose existence postponed
                        # execution for this task have expired.

                        # We will now set the expiration on this key to expire
                        # at the time of the next appropriate running of this task

                        REDIS.expire(stop_key, int(float((expire_key-now).total_seconds())))

                        #queue it up
                        task.soon()

                        logger.debug('next will be: %r', expire_key)

                except redis.exceptions.ResponseError as e:
                    print e
                except BaseException as e:
                    print e

        try:
            for g in TASK_GROUPS:
                if not self.active_task:
                    task = REDIS.lpop(g)
                    if task:
                        # chalk.yellow('RUNNING TASK on thread %r: %s' % (self, task))
                        logger.debug('RUNNING TASK on thread %r: %s' % (self, task))
                        self.active_task = True
                        threads.deferToThread(run_task, task, self)

        except BaseException as e:
            chalk.red('%s got an error' % self)
            print traceback.format_exc()

    def cleanup(self):
        pass
        # print 'thread %d cleaning up' % thread



    def start(self):
        task.LoopingCall(self.control).start(INTERVAL)

def run_task(task, thread):

    task = Task.rehydrate(task)
    chalk.yellow('%r: %s'%(thread,task.key))
    with CaptureStdOut(task=task) as output:
        try:
            task.run()
        except:
            print traceback.format_exc()
    output.finished()

    thread.active_task = False


if THREAD_COUNT:
    chalk.green('current time: %r'%utc_now())
    chalk.green('Found %d thread(s) specified in settings.TIEMPO_THREADS'%THREAD_COUNT)

    for i in range(0,THREAD_COUNT):
        tm = ThreadManager(i)
        tm.start()

def auto_load_tasks():
    for app in settings.PROJECT_APPS:
        module = importlib.import_module(app)
        try:
            importlib.import_module(app+'.tasks')
            chalk.blue('imported tasks from %s'%app)
        except ImportError as e:
            # print traceback.format_exc() 
            pass
    if settings.DEBUG:
        pass
        # import tasks

auto_load_tasks()
