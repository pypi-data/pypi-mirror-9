# -*- coding: utf-8 -*-

import logging
import jsonschema
import iso8601

from datetime import datetime
from .fields import MsgFields as F, MsgErrs as MERR
from .exceptions import ValidationError
import schemas


log = logging.getLogger(__name__)

SEED_VERSION = "9.9.9"


def iso_now():
    return datetime.utcnow().isoformat()


class TaskResult(dict):
    """
    TaskResult represents a Task result for a single Target Monitoring Object
    (TMO). It's designed to be used inside task functions like this:

    tr = TaskResult("mytask", "2.2.5", 1111)
    tr.add("analysis", [1, 2, 3])
    tr.finish()

    This also adds a variety of metadata, like task run times and errors.
    """

    reserved_keys = [F.META]

    def __init__(self, output_name, tmoid, task_name, task_version,
                 agent_name=None, data=None, schema=None):
        # str name of output type this TaskResult generated Not used
        # internally, but referenced when adding to TaskResults.
        self.output_name = output_name
        # int with the id of the target monitor object Not used internally, but
        # referenced when adding to TaskResults.
        self.tmoid = tmoid
        # agent that fulfiled this request
        self.__agent_name = agent_name
        # str name of the task generating this output.
        self.__task_name = task_name
        # Supplied by task.
        self.__task_version = task_version

        # Should be class of type colander.Schema.
        # Chiefly for testing - by default, will look for corresponding
        # schema to task_name
        self.schema = self._set_schema(schema)

        if not self.output_name:
            raise ValueError("Must define an output type")
        if not self.__task_name:
            raise ValueError("Must define a task type")
        if (not self.__task_version or
                not isinstance(self.__task_version, basestring)):
            raise ValueError("Must define a task version as a string "
                             "(e.g. '1.2.2.'")

        try:
            self.tmoid = str(int(self.tmoid))
        except TypeError:
            raise ValueError("Target monitoring id (tmoid) must be an int: "
                             "got %s of type %s"
                             % (self.tmoid, type(self.tmoid)))

        # start the timer
        self._time_start = iso_now()
        self._time_end = None

        dict.__init__(self)

        if data and not isinstance(data, dict):
            raise ValueError("data must be a dictionary to import")
        elif data:
            self.update(data)

    @classmethod
    def init_from_dict(cls, output_name, tmoid, data, schema=None):
        """
        Load a TaskResult from a dict, likely a deserialized TaskResult from
        somewhere else. Note that task_version is contained in the meta data
        already, so we don't pass it in.
        """
        # str name of the task's output
        task_version = None
        # int with the id of the target monitor object

        try:
            task_name = data[F.META][F.META_TASK_NAME]
            task_version = data[F.META][F.META_TASK_VERSION]
            agent_name = data[F.META].get(F.META_AGENT_NAME)
        except KeyError:
            raise ValueError("TaskResult dict does not define a version "
                             "number")
        return cls(output_name, tmoid, task_name, task_version,
                   agent_name=agent_name, data=data, schema=schema)

    def _set_schema(self, supplied_schema):
        """
        Automatically select a JSON schema to validate this TaskResult.
        This is either based on the task_name (e.g. if task_name is abc,
        _set_schema will attempt to load AbcSchema, or load a schema manually
        supplied).
        """
        schema_cls = None

        if not self.output_name:
            raise ValueError("Must specify a task_name")

        if not supplied_schema:
            log.debug("Output name: {0}".format(self.output_name))
            log.debug("Output name title: {0}"
                      .format(self.output_name.title()))
            schema_name = "{0}Schema".format(self.output_name.title())
            try:
                schema_cls = getattr(schemas, schema_name)
            except AttributeError:
                raise ValueError("Couldn't find validation schema called {0}"
                                 .format(schema_name))
        else:
            schema_cls = supplied_schema

        return schema_cls

    def add(self, result_name, result_val):
        """
        Add a named result to the TaskResult.
        """
        if result_name in self.reserved_keys:
            raise ValueError("{0} is a reserved key name - please choose"
                             " another.".format(result_name))

        if not result_name:
            raise ValueError("key must be a defined value")

        self.setdefault(result_name, result_val)

    def get_data_strict(self, key):
        """
        Find and return a data key, raise ValueError if not found
        """
        try:
            return self[key]
        except KeyError:
            log.debug(self)
            raise ValueError("{0}.{1} has no value for {2}".format(
                self.output_name, self.tmoid, key))

    def get_data(self, key):
        """
        Find and return a data key, return None if not found
        """
        return self.get(key, None)

    def get_meta(self, key):
        """
        Return a meta field from this Task
        """
        return self[F.META].get(key)

    @property
    def success(self):
        """
        Return true if the task returned with no errors
        """
        return self.err is None

    @property
    def err(self):
        """
        Return errors returned by a task
        """
        try:
            return self[F.META][F.META_ERR]
        except KeyError:
            return

    @property
    def msg(self):
        """
        Return diagnostic messages returned by a task
        """
        try:
            return self[F.META][F.META_MSG]
        except KeyError:
            return

    @property
    def agent_name(self):
        """
        Return name of agent executing task
        """
        try:
            return self[F.META][F.META_AGENT_NAME]
        except KeyError:
            return

    @property
    def task_name(self):
        """
        Return task name that executed
        """
        try:
            return self[F.META][F.META_TASK_NAME]
        except KeyError:
            return

    @property
    def task_version(self):
        """
        Return errors returned by a task
        """
        try:
            return self[F.META][F.META_TASK_VERSION]
        except KeyError:
            return

    @property
    def time_start_iso(self):
        """
        Return start time for a task
        """
        try:
            return self[F.META][F.META_START_TIME]
        except KeyError:
            return

    @property
    def time_start(self):
        return iso8601.parse_date(self.time_start_iso)

    @property
    def time_end_iso(self):
        """
        Return start time for a task
        """
        try:
            return self[F.META][F.META_END_TIME]
        except KeyError:
            return

    @property
    def time_end(self):
        return iso8601.parse_date(self.time_end_iso)

    def finish(self, err=None, msg=None):
        """
        Add the result for the event, any error messages, and stop the timer
        """
        self._time_end = iso_now()

        self.setdefault(F.META, {})
        self[F.META][F.META_ERR] = err
        self[F.META][F.META_MSG] = msg
        self[F.META][F.META_START_TIME] = self._time_start
        self[F.META][F.META_END_TIME] = self._time_end
        self[F.META][F.META_AGENT_NAME] = self.__agent_name
        self[F.META][F.META_TASK_NAME] = self.__task_name
        self[F.META][F.META_TASK_VERSION] = self.__task_version

        try:
            self.schema_validate()
        except ValidationError as e:
            # The original error may have caused schema non-validation.
            # Leave original error if exists, otherwise, add schema err.
            if not self[F.META][F.META_ERR]:
                self[F.META][F.META_ERR] = MERR.RESULT_INVALID.format(e)

        if self.err:
            log.debug(self.err)

    def schema_validate(self):
        try:
            jsonschema.validate(self, self.schema)
        except Exception as e:
            log.debug(self)
            raise ValidationError(
                "Couldn't validate under {0} schema: {1}"
                .format(self, e)
            )


class TaskSeed(TaskResult):
    def __init__(self, output_name, tmoid, key, val):
        super(TaskSeed, self).__init__(output_name, tmoid, F.SEEDED_TASK,
                                       SEED_VERSION)
        self.add(key, val)
        self.finish()
