
"""
Manager for devices
"""

import sys
import six
import logging

from celery import states
from celery import Celery
from celery.result import AsyncResult
from celery.backends.base import DisabledBackend

from control_client.common import importutils

LOG = logging.getLogger(__name__)

ROBOTICE_LIB = False

try:
    sys.path.append("/srv/robotice/service")
    import robotice
    ROBOTICE_LIB = True
except Exception, e:
    pass

from control_client.robotice.managers import base

LOG = logging.getLogger(__name__)

class TaskManager(base.RoboticeManager):

    def list(self):
        """
        Returns a list of celery tasks.
        """

        limit = limit and int(limit)
        worker = worker if worker != 'All' else None
        type = type if type != 'All' else None
        state = state if state != 'All' else None

        app = self.app(role)

        events = app.events.State()

        result = []
        for task_id, task in tasks.iter_tasks(
                events, limit=limit, type=type,
                worker=worker, state=state):
            task = task.as_dict()
            task.pop('worker')
            result.append((task_id, task))

        return result


    def create_or_update(self, id, item):
        raise NotImplementedError

    def get(self, id):
        raise NotImplementedError

    def backend_configured(self, result):
        return not isinstance(result.backend, DisabledBackend)

    def app(self, name=None, default=False):
        """celery app
        """
        if default and name is None:
            mod = self.find_some_worker()
            return self.load_app(mod)

        conf = importutils.import_module("robotice.worker_%s" % name)

        return self.load_app(conf)


    def _get_task_args(self, body):
        """helper which return task args, kwargs and options
        """

        try:
            options = body
            if isinstance(body, basestring):
                options = json.loads(body)
            args = options.pop('args', [])
            kwargs = options.pop('kwargs', {})
        except Exception, e:
            raise e

        if not isinstance(args, (list, tuple)):
            try:
                args = args.values()
                return args, kwargs, options
            except Exception, e:
                raise e
            raise exc.HTTPBadRequest('args must be an array')

        return args, kwargs, options

    @staticmethod
    def load_app(module):
        """load celery app from config file
        """

        app = Celery(module.__name__)
        app.config_from_object(module)

        return app

    def find_some_worker(self):
        """ this method find first available worker
        """

        for worker in ["reasoner", "planer", "monitor", "reactor"]:

            try:
                conf = importutils.import_module("robotice.worker_%s" % worker)
                return conf
            except ImportError:
                raise e

        return None

    def send(self, taskname=None, body={}, role=None, **kwargs):

        app = self.app(role, default=True)

        args, kwargs, options = self._get_task_args(body)
        LOG.debug("Invoking task '%s' with '%s' and '%s'",
                  taskname, args, kwargs)

        result = app.send_task(
            taskname, args=args, kwargs=kwargs, **options)
        response = {'task-id': result.task_id}

        if self.backend_configured(result):
            response.update(state=result.state)

        return response


    def result(self, task_id):
        result = AsyncResult(task_id)

        if not self.backend_configured(result):
            raise exc.HTTPBadRequest(
                "backend disabled ! maybe set CELERY_RESULT_BACKEND fix this issue")
        response = {'task-id': task_id, 'state': result.state}
        if result.ready():
            if result.state == states.FAILURE:
                response.update({'result': result.result,
                                 'traceback': result.traceback})
            else:
                response.update({'result': result.result})

        return response


    def info(self, task_id):

        app = self.app(role)
        events = app.events.State()

        task = tasks.get_task_by_id(events, task_id)
        if not task:
            raise exc.HTTPNotFound("Unknown task '%s'" % task_id)
        response = {}
        for name in task._fields:
            if name not in ['uuid', 'worker']:
                response[name] = getattr(task, name, None)
        response['task-id'] = task.uuid
        response['worker'] = task.worker.hostname

        return response

tasks = TaskManager()