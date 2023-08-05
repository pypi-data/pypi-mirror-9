# -*- coding: utf-8 -*-

import logging
import unittest
import json
from freezegun import freeze_time
from datetime import datetime, timedelta
from pytz import utc

from ..taskresult import TaskResult, TaskSeed, SEED_VERSION
from ..fields import MsgFields as F, MsgErrs as MERR
from ..schemas import build_schema


class TestTaskResult(unittest.TestCase):
    def setUp(self):
        self.output_name = "test"
        self.task_name = "test_task"

    def test_init(self):
        m = TaskResult(self.output_name, 111, self.task_name, "1.1.1")
        self.assertIsNotNone(m)

    def test_missing_taskid(self):
        tr = None
        try:
            tr = TaskResult(self.output_name, 111, None, "1.1.1")
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_missing_task_version(self):
        tr = None
        try:
            tr = TaskResult(self.output_name, 111, self.task_name, None)
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_non_str_task_version(self):
        tr = None
        try:
            tr = TaskResult(self.output_name, 111, self.task_name, 1.1)
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_missing_tmoid(self):
        tr = None
        try:
            tr = TaskResult(self.output_name, None, self.task_name, "1.1.1")
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_non_numeric_tmoid(self):
        tr = None
        try:
            tr = TaskResult(self.output_name, "abc", self.task_name, "1.1.1")
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_add(self):
        tr = TaskResult(self.output_name, 38974823, self.task_name, "1.1.1")
        tr.add("a", "Here are my results")
        self.assertEqual(tr.get_data("a"), "Here are my results")

    def test_add_nested_data(self):
        tr = TaskResult(self.output_name, 10098, self.task_name, "1.1.1")
        tr.add("results", {"a": "Nested"})
        self.assertEqual(tr.get_data("results"), {"a": "Nested"})

    def test_missing_data(self):
        tr = TaskResult(self.output_name, 10098, self.task_name, "1.1.1")
        tr.add("a", "Here are my results")
        self.assertIsNone(tr.get_data("nothere"))

    def test_missing_data_strict(self):
        tr = TaskResult(self.output_name, 10098, self.task_name, "1.1.1")
        tr.add("a", "Here are my results")
        try:
            tr.get_data_strict("nothere")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_dict_loop(self):
        tr = TaskResult(self.output_name, 8734, self.task_name, "1.1.1")
        tr.add("a", "1")
        tr.add("b", "2")
        self.assertEqual(set(tr.keys()), set(["a", "b"]))

    def test_multi_key(self):
        tr = TaskResult(self.output_name, 8734, self.task_name, "1.1.1")
        tr.add("a", "1")
        tr.add("b", "2")
        tr.finish()

        self.assertEqual(tr.get_data("a"), "1")
        self.assertEqual(tr.get_data("b"), "2")

    def test_finalise_success(self):
        tr = TaskResult(self.output_name, 123, self.task_name, "1.1.1")
        tr.add("a", "result")
        tr.finish()
        self.assertEqual(tr.success, True)

    def test_finalise_failure(self):
        tr = TaskResult(self.output_name, 123, self.task_name, "1.1.1")
        tr.add("a", "result")
        tr.finish(err="Everything broken")
        self.assertFalse(tr.success)
        self.assertIsNotNone(tr.err)

    def test_timer_success(self):
        base_time = datetime(2016, 01, 01, 0, 0, 0)

        with freeze_time(base_time):
            tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
            tr.add("a", "My whois data")
        with freeze_time(base_time + timedelta(seconds=2)):
            tr.finish()
        logging.debug(tr)
        self.assertIsNotNone(tr.time_end)
        self.assertLess(tr.time_start, tr.time_end)

    def test_timer_on_error(self):
        base_time = datetime(2016, 01, 01, 0, 0, 0)

        with freeze_time(base_time):
            tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
            tr.add("a", "My whois data")
        with freeze_time(base_time + timedelta(seconds=2)):
            tr.finish(err="Everything broke")

        self.assertIsNotNone(tr.time_end)
        self.assertLess(tr.time_start, tr.time_end)

    def test_success(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
        tr.add("a", "My whois data")
        tr.finish()
        self.assertTrue(tr.success)
        self.assertIsNone(tr.err)

    def test_failure(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
        tr.add("a", "My whois data")
        tr.finish(err="Everything broke")
        self.assertFalse(tr.success)
        self.assertEqual(tr.err, "Everything broke")

    def test_msg(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
        tr.add("a", "My whois data")
        tr.finish(msg="Diagnostic info")
        self.assertEqual(tr[F.META][F.META_MSG], "Diagnostic info")

    def test_reserved_name(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
        try:
            tr.add(F.META, "Reserved field")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_version(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "3.4.5")
        tr.add("a", "result")
        tr.finish()

        self.assertEqual(tr.task_version, "3.4.5")

    def test_agent_name_none(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "3.4.5")
        tr.add("a", "result")
        tr.finish()

        self.assertEqual(tr.agent_name, None)

    def test_agent_name(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "3.4.5",
                        agent_name="agent1")
        tr.add("a", "result")
        tr.finish()

        self.assertEqual(tr.agent_name, "agent1")

    def test_obj_json_import(self):
        base_time = datetime(2016, 01, 01, 0, 0, 0)

        with freeze_time(base_time):
            tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
            tr.add("a", "My whois data")
            tr.finish(err="Everything broke")

        tr_json = json.dumps(tr)
        logging.debug(tr_json)
        tr2 = TaskResult.init_from_dict(self.output_name,
                                        100, json.loads(tr_json))
        self.assertEqual(tr2.get_data("a"), "My whois data")
        self.assertFalse(tr2.success)
        self.assertEqual(tr2.err, "Everything broke")
        self.assertEqual(tr2.task_name, self.task_name)
        self.assertEqual(tr2.output_name, self.output_name)
        self.assertEqual(tr2.task_version, "1.1.1")
        self.assertEqual(tr2.time_start, base_time.replace(tzinfo=utc))
        self.assertEqual(tr2.time_end, base_time.replace(tzinfo=utc))

    def test_obj_json_import_with_agent(self):
        base_time = datetime(2016, 01, 01, 0, 0, 0)

        with freeze_time(base_time):
            tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1",
                            agent_name="agent1")
            tr.add("a", "My whois data")
            tr.finish()

        tr_json = json.dumps(tr)
        logging.debug(tr_json)
        tr2 = TaskResult.init_from_dict(self.output_name,
                                        100, json.loads(tr_json))
        logging.debug(tr2)
        self.assertEqual(tr2.get_data("a"), "My whois data")
        self.assertTrue(tr2.success)
        self.assertEqual(tr2.err, None)
        self.assertEqual(tr2.agent_name, "agent1")
        self.assertEqual(tr2.task_name, self.task_name)
        self.assertEqual(tr2.output_name, self.output_name)
        self.assertEqual(tr2.task_version, "1.1.1")
        self.assertEqual(tr2.time_start, base_time.replace(tzinfo=utc))
        self.assertEqual(tr2.time_end, base_time.replace(tzinfo=utc))

    def test_schema_fail(self):
        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1")
        tr.add("nosuch", "My whois data")
        tr.finish()

        self.assertFalse(tr.success)
        self.assertTrue(tr.err.startswith(MERR.RESULT_INVALID.format("")))

    def test_custom_schema(self):
        TestCustomSchema = build_schema({
            "properties": {
                "z": {"type": "string"}
            },
            "required": ["z"]
        })

        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1",
                        schema=TestCustomSchema)
        tr.add("z", "My whois data")
        tr.finish()

        self.assertEqual(tr.get_data("z"), "My whois data")

    def test_custom_schema_invalid(self):
        TestCustomInvalidSchema = build_schema({
            "properties": {
                "z": {"type": "string"}
            },
            "required": ["z"]
        })

        tr = TaskResult(self.output_name, 100, self.task_name, "1.1.1",
                        schema=TestCustomInvalidSchema)
        tr.add("y", "My whois data")
        tr.finish()

        self.assertFalse(tr.success)
        self.assertTrue(tr.err.startswith(MERR.RESULT_INVALID.format("")))


class TestTaskSeed(unittest.TestCase):
    def setUp(self):
        self.output_name = "test"

    def test_taskseed_payload(self):
        ts = TaskSeed(self.output_name, 100, "a", "example.com")
        self.assertEqual(ts.get_data("a"), "example.com")

    def test_taskseed_task_name(self):
        ts = TaskSeed(self.output_name, 100, "a", "example.com")
        self.assertEqual(ts.task_name, F.SEEDED_TASK)

    def test_taskseed_version(self):
        ts = TaskSeed(self.output_name, 100, "a", "example.com")
        self.assertEqual(ts.task_version, SEED_VERSION)

    def test_taskseed_dates(self):
        ts = TaskSeed(self.output_name, 100, "a", "example.com")
        self.assertIsNotNone(ts.get_meta(F.META_START_TIME))
        self.assertIsNotNone(ts.get_meta(F.META_END_TIME))
