# -*- coding: utf-8 -*-

from .taskresult import TaskResult
from .fields import MsgFields as MSGF, MsgErrs as MERR
from .exceptions import TaskResultFailException


class TaskResultSet(dict):
    """
    JobResult is a dict for storing TaskResults with convenience functions.
    """
    def __init__(self, target_id, job_id, data=None):
        self.setdefault(MSGF.TRS_META, {})

        # target_id and job_id are stored internally as strs, since this
        # is how they get json encoded. To API user, they're converted to
        # ints when using .target_id, .job_id, get_task_tmoid() etc.
        try:
            target_id = str(int(target_id))
        except TypeError:
            raise ValueError("Target id must be a number")

        try:
            job_id = str(int(job_id))
        except TypeError:
            raise ValueError("Job id must be a number")

        self[MSGF.TRS_META][MSGF.TRS_META_TARGET_ID] = target_id
        self[MSGF.TRS_META][MSGF.TRS_META_JOB_ID] = job_id

        dict.__init__(self)

        if data and not isinstance(data, dict):
            raise ValueError("data must be a dictionary to import")
        elif data:
            self.update(data)

    @classmethod
    def init_from_dict(cls, data):
        """
        Init a TaskResult set from a a (likely JSON deserialized) dict.
        """
        target_id = data[MSGF.TRS_META][MSGF.TRS_META_TARGET_ID]
        job_id = data[MSGF.TRS_META][MSGF.TRS_META_JOB_ID]

        return cls(target_id, job_id, data=data)

    @property
    def target_id(self):
        """
        Return an int representing target_id of Job.
        """
        try:
            return int(self[MSGF.TRS_META][MSGF.TRS_META_TARGET_ID])
        except KeyError:
            raise ValueError("Target ID not set!")
        except TypeError:
            raise ValueError("Target ID muse be an int")

    @property
    def job_id(self):
        """
        Return an int representing job_id of Job.
        """
        try:
            return int(self[MSGF.TRS_META][MSGF.TRS_META_JOB_ID])
        except KeyError:
            raise ValueError("Job ID not set!")
        except TypeError:
            raise ValueError("Job ID must be an int")

    def add(self, task_result):
        """
        Add a TaskResult to this TaskResultSet.
        """
        missed_field_err = ("TaskResult must specify a {0}. Did you remember "
                            "to finish() the task?")

        if not task_result.output_name:
            raise ValueError(missed_field_err.format("output_name"))
        if not task_result.task_name:
            raise ValueError(missed_field_err.format("task_name"))
        if not task_result.task_version:
            raise ValueError(missed_field_err.format("task_version"))
        if not task_result.tmoid:
            raise ValueError(missed_field_err.format(
                "task monitoring object id"))

        self.setdefault(task_result.output_name, {
            MSGF.TASKRESULTS: {},
            MSGF.META: {}}
        )
        self[task_result.output_name][MSGF.TASKRESULTS][task_result.tmoid] = \
            dict(task_result)

    def add_output_err(self, output_name, err):
        """
        Add an error indicating that there was a TaskResult-level error
        preventing Task from being run (e.g. insufficient inputs)
        Use TaskResult.err when this problem relates to a particular tmoid,
        and TaskResultSet.add_task_err() when none of the tmoids could be
        tested.
        """
        self.setdefault(output_name, {MSGF.TASKRESULTS: {}, MSGF.META: {}})

        self[output_name][MSGF.META].setdefault(MSGF.META_ERR, [])

        self[output_name][MSGF.META][MSGF.META_ERR].append(err)

    def output_success(self, output_name):
        """
        Return a bool indicating if a TaskResult ran without high-level
        errors i.e. testing was attempted for tmoids.
        """
        return self.output_errs(output_name) == []

    def output_errs(self, output_name):
        """
        Return list of errors returned by an output's task.
        """
        try:
            self[output_name][MSGF.META]
        except:
            raise ValueError("%s output not found in message" % output_name)

        return self[output_name][MSGF.META].get(MSGF.META_ERR, [])

    def outputs(self):
        """
        Return a list of outputs contained in a message.
        """
        return filter(lambda k: k != MSGF.TRS_META, self.iterkeys())

    def output_tmoids(self, output_name):
        """
        Return a list of tmoid ints related to a Task result name.
        """
        try:
            self[output_name][MSGF.TASKRESULTS]
        except KeyError:
            raise ValueError("%s task not found in message" % output_name)

        # keys here are json encoded as strs, recast to int
        return [int(k) for k in self[output_name][MSGF.TASKRESULTS].keys()]

    def get_output_tmoid(self, output_name, tmoid, schema=None):
        """
        Get a single TaskResult based on a task name and target monitoring
        ID. Raises exceptions if output_name or tmoid not found.
        Use when you want to get the result back, even if it's failed.
        """
        try:
            tmoid = str(int(tmoid))
        except TypeError:
            raise ValueError("Tmoid must be an int")

        try:
            self[output_name][MSGF.TASKRESULTS][tmoid]
        except KeyError:
            raise ValueError("Could not find output {0} with tmoid {1} in "
                             "results".format(output_name, tmoid))

        tr = TaskResult.init_from_dict(
            output_name,
            tmoid,
            self[output_name][MSGF.TASKRESULTS][tmoid],
            schema=schema
        )

        return tr

    def get_output_tmoid_raise_fail(self, output_name, tmoid, schema=None):
        """
        Returns a TaskResult and error string tuple given output_name and
        tmoid.
        Returns None for TaskResult if there was any problem with the
        TaskResult.
        Use when you want a hard raise when a task result failed.
        """
        try:
            tr = self.get_output_tmoid(output_name, tmoid, schema=schema)
            if not tr.success:
                raise TaskResultFailException(
                    MERR.RESULT_FAIL.format(tr.err))
            return tr
        except Exception:
            raise

    def get_output_tmoid_or_none(self, output_name, tmoid, schema=None):
        """
        Returns a TaskResult and error string tuple given output_name and
        tmoid.
        Returns None for TaskResult if there was any problem with the
        TaskResult.
        Use when you want a soft failure when a task failed.
        """
        tr = None
        err = None

        try:
            tr = self.get_output_tmoid_raise_fail(
                output_name, tmoid, schema=schema)
        except Exception as e:
            err = e
        return ((tr, err))
