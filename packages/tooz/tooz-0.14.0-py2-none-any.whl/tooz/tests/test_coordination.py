# -*- coding: utf-8 -*-
#
#    Copyright © 2013-2015 eNovance Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
import threading
import time
import uuid

from concurrent import futures
import testscenarios
from testtools import matchers
from testtools import testcase

import tooz.coordination
from tooz import tests


def try_to_lock_job(name, coord, url, member_id):
    if not coord:
        coord = tooz.coordination.get_coordinator(
            url, member_id)
        coord.start()
    lock2 = coord.get_lock(name)
    return lock2.acquire(blocking=False)


class TestAPI(testscenarios.TestWithScenarios,
              tests.TestCaseSkipNotImplemented):

    scenarios = [
        ('kazoo', {'url': os.getenv("TOOZ_TEST_ZOOKEEPER_URL"),
                   'bad_url': 'kazoo://localhost:1'}),
        ('zake', {'url': 'zake://?timeout=5'}),
        ('memcached', {'url': os.getenv("TOOZ_TEST_MEMCACHED_URL"),
                       'bad_url': 'memcached://localhost:1',
                       'timeout_capable': True}),
        ('ipc', {'url': 'ipc://'}),
        ('file', {'url': 'file:///tmp'}),
        ('redis', {'url': os.getenv("TOOZ_TEST_REDIS_URL"),
                   'bad_url': 'redis://localhost:1',
                   'timeout_capable': True}),
        ('postgresql', {'url': os.getenv("TOOZ_TEST_PGSQL_URL"),
                        'bad_url': 'postgresql://localhost:1'}),
        ('mysql', {'url': os.getenv("TOOZ_TEST_MYSQL_URL"),
                   'bad_url': 'mysql://localhost:1'}),
    ]

    def assertRaisesAny(self, exc_classes, callable_obj, *args, **kwargs):
        checkers = [matchers.MatchesException(exc_class)
                    for exc_class in exc_classes]
        matcher = matchers.Raises(matchers.MatchesAny(*checkers))
        callable_obj = testcase.Nullary(callable_obj, *args, **kwargs)
        self.assertThat(callable_obj, matcher)

    def setUp(self):
        super(TestAPI, self).setUp()
        if self.url is None:
            self.skipTest("No URL set for this driver")
        self.group_id = self._get_random_uuid()
        self.member_id = self._get_random_uuid()
        self._coord = tooz.coordination.get_coordinator(self.url,
                                                        self.member_id)
        self._coord.start()

    def tearDown(self):
        self._coord.stop()
        super(TestAPI, self).tearDown()

    def test_connection_error(self):
        if not hasattr(self, "bad_url"):
            raise testcase.TestSkipped("No bad URL provided")
        coord = tooz.coordination.get_coordinator(self.bad_url,
                                                  self.member_id)
        self.assertRaises(tooz.coordination.ToozConnectionError,
                          coord.start)

    def test_stop_first(self):
        c = tooz.coordination.get_coordinator(self.url,
                                              self.member_id)
        self.assertRaises(tooz.coordination.ToozError,
                          c.stop)

    def test_create_group(self):
        self._coord.create_group(self.group_id).get()
        all_group_ids = self._coord.get_groups().get()
        self.assertTrue(self.group_id in all_group_ids)

    def test_create_group_already_exist(self):
        self._coord.create_group(self.group_id).get()
        create_group = self._coord.create_group(self.group_id)
        self.assertRaises(tooz.coordination.GroupAlreadyExist,
                          create_group.get)

    def test_get_groups(self):
        groups_ids = [self._get_random_uuid() for _ in range(0, 5)]
        for group_id in groups_ids:
            self._coord.create_group(group_id).get()
        created_groups = self._coord.get_groups().get()
        for group_id in groups_ids:
            self.assertTrue(group_id in created_groups)

    def test_delete_group(self):
        self._coord.create_group(self.group_id).get()
        all_group_ids = self._coord.get_groups().get()
        self.assertTrue(self.group_id in all_group_ids)
        self._coord.delete_group(self.group_id).get()
        all_group_ids = self._coord.get_groups().get()
        self.assertFalse(self.group_id in all_group_ids)
        join_group = self._coord.join_group(self.group_id)
        self.assertRaises(tooz.coordination.GroupNotCreated,
                          join_group.get)

    def test_delete_group_non_existent(self):
        delete = self._coord.delete_group(self.group_id)
        self.assertRaises(tooz.coordination.GroupNotCreated,
                          delete.get)

    def test_delete_group_non_empty(self):
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id).get()
        delete = self._coord.delete_group(self.group_id)
        self.assertRaises(tooz.coordination.GroupNotEmpty,
                          delete.get)
        self._coord.leave_group(self.group_id)
        self._coord.delete_group(self.group_id).get()

    def test_join_group(self):
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id).get()
        member_list = self._coord.get_members(self.group_id).get()
        self.assertTrue(self.member_id in member_list)

    def test_join_nonexistent_group(self):
        join_group = self._coord.join_group(self.group_id)
        self.assertRaises(tooz.coordination.GroupNotCreated,
                          join_group.get)

    def test_join_group_with_member_id_already_exists(self):
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id).get()
        client = tooz.coordination.get_coordinator(self.url,
                                                   self.member_id)
        client.start()
        join_group = client.join_group(self.group_id)
        self.assertRaises(tooz.coordination.MemberAlreadyExist,
                          join_group.get)

    def test_leave_group(self):
        self._coord.create_group(self.group_id).get()
        all_group_ids = self._coord.get_groups().get()
        self.assertTrue(self.group_id in all_group_ids)
        self._coord.join_group(self.group_id).get()
        member_list = self._coord.get_members(self.group_id).get()
        self.assertTrue(self.member_id in member_list)
        member_ids = self._coord.get_members(self.group_id).get()
        self.assertTrue(self.member_id in member_ids)
        self._coord.leave_group(self.group_id).get()
        new_member_objects = self._coord.get_members(self.group_id).get()
        new_member_list = [member.member_id for member in new_member_objects]
        self.assertTrue(self.member_id not in new_member_list)

    def test_leave_nonexistent_group(self):
        all_group_ids = self._coord.get_groups().get()
        self.assertTrue(self.group_id not in all_group_ids)
        leave_group = self._coord.leave_group(self.group_id)
        # Drivers raise one of those depending on their capability
        self.assertRaisesAny([tooz.coordination.MemberNotJoined,
                              tooz.coordination.GroupNotCreated],
                             leave_group.get)

    def test_leave_group_not_joined_by_member(self):
        self._coord.create_group(self.group_id).get()
        all_group_ids = self._coord.get_groups().get()
        self.assertTrue(self.group_id in all_group_ids)
        leave_group = self._coord.leave_group(self.group_id)
        self.assertRaises(tooz.coordination.MemberNotJoined,
                          leave_group.get)

    def test_get_members(self):
        group_id_test2 = self._get_random_uuid()
        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()

        self._coord.create_group(group_id_test2).get()
        self._coord.join_group(group_id_test2).get()
        client2.join_group(group_id_test2).get()
        members_ids = self._coord.get_members(group_id_test2).get()
        self.assertTrue(self.member_id in members_ids)
        self.assertTrue(member_id_test2 in members_ids)

    def test_get_member_capabilities(self):
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id, b"test_capabilities")

        capa = self._coord.get_member_capabilities(self.group_id,
                                                   self.member_id).get()
        self.assertEqual(capa, b"test_capabilities")

    def test_get_member_capabilities_complex(self):
        self._coord.create_group(self.group_id).get()
        caps = {
            'type': 'warrior',
            'abilities': ['fight', 'flight', 'double-hit-damage'],
        }
        self._coord.join_group(self.group_id, caps)
        capa = self._coord.get_member_capabilities(self.group_id,
                                                   self.member_id).get()
        self.assertEqual(capa, caps)

    def test_get_member_capabilities_nonexistent_group(self):
        capa = self._coord.get_member_capabilities(self.group_id,
                                                   self.member_id)
        # Drivers raise one of those depending on their capability
        self.assertRaisesAny([tooz.coordination.MemberNotJoined,
                              tooz.coordination.GroupNotCreated],
                             capa.get)

    def test_get_member_capabilities_nonjoined_member(self):
        self._coord.create_group(self.group_id).get()
        capa = self._coord.get_member_capabilities(self.group_id,
                                                   self.member_id)
        self.assertRaises(tooz.coordination.MemberNotJoined,
                          capa.get)

    def test_update_capabilities(self):
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id, b"test_capabilities1").get()

        capa = self._coord.get_member_capabilities(self.group_id,
                                                   self.member_id).get()
        self.assertEqual(capa, b"test_capabilities1")
        self._coord.update_capabilities(self.group_id,
                                        b"test_capabilities2").get()

        capa2 = self._coord.get_member_capabilities(self.group_id,
                                                    self.member_id).get()
        self.assertEqual(capa2, b"test_capabilities2")

    def test_update_capabilities_with_group_id_nonexistent(self):
        update_cap = self._coord.update_capabilities(self.group_id,
                                                     b'test_capabilities')
        # Drivers raise one of those depending on their capability
        self.assertRaisesAny([tooz.coordination.MemberNotJoined,
                              tooz.coordination.GroupNotCreated],
                             update_cap.get)

    def test_heartbeat(self):
        self._coord.heartbeat()

    def test_disconnect_leave_group(self):
        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id).get()
        client2.join_group(self.group_id).get()
        members_ids = self._coord.get_members(self.group_id).get()
        self.assertTrue(self.member_id in members_ids)
        self.assertTrue(member_id_test2 in members_ids)
        client2.stop()
        members_ids = self._coord.get_members(self.group_id).get()
        self.assertTrue(self.member_id in members_ids)
        self.assertTrue(member_id_test2 not in members_ids)

    def test_timeout(self):
        if not getattr(self, "timeout_capable", False):
            self.skipTest("This test only works with timeout capable drivers")
        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id).get()
        client2.join_group(self.group_id).get()
        members_ids = self._coord.get_members(self.group_id).get()
        self.assertTrue(self.member_id in members_ids)
        self.assertTrue(member_id_test2 in members_ids)

        # Watch the group, we want to be sure that when client2 is kicked out
        # we get an event.
        self._coord.watch_leave_group(self.group_id, self._set_event)

        time.sleep(3)
        self._coord.heartbeat()
        time.sleep(3)

        # Now client2 has timed out!

        members_ids = self._coord.get_members(self.group_id).get()
        while True:
            if self._coord.run_watchers():
                break
        self.assertTrue(self.member_id in members_ids)
        self.assertTrue(member_id_test2 not in members_ids)
        # Check that the event has been triggered
        self.assertIsInstance(self.event,
                              tooz.coordination.MemberLeftGroup)
        self.assertEqual(member_id_test2,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

    def _set_event(self, event):
        self.event = event
        return 42

    def test_watch_group_join(self):
        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        self._coord.create_group(self.group_id).get()

        # Watch the group
        self._coord.watch_join_group(self.group_id, self._set_event)

        # Join the group
        client2.join_group(self.group_id).get()
        members_ids = self._coord.get_members(self.group_id).get()
        self.assertTrue(member_id_test2 in members_ids)
        while True:
            if self._coord.run_watchers():
                break
        self.assertIsInstance(self.event,
                              tooz.coordination.MemberJoinedGroup)
        self.assertEqual(member_id_test2,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

        # Stop watching
        self._coord.unwatch_join_group(self.group_id, self._set_event)
        self.event = None

        # Leave and rejoin group
        client2.leave_group(self.group_id).get()
        client2.join_group(self.group_id).get()
        self._coord.run_watchers()
        self.assertIsNone(self.event)

    def test_watch_leave_group(self):
        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        self._coord.create_group(self.group_id).get()

        # Watch the group: this can leads to race conditions in certain
        # driver that are not able to see all events, so we join, wait for
        # the join to be seen, and then we leave, and wait for the leave to
        # be seen.
        self._coord.watch_join_group(self.group_id, lambda children: True)
        self._coord.watch_leave_group(self.group_id, self._set_event)

        # Join and leave the group
        client2.join_group(self.group_id).get()
        # Consumes join event
        while True:
            if self._coord.run_watchers():
                break
        client2.leave_group(self.group_id).get()
        # Consumes leave event
        while True:
            if self._coord.run_watchers():
                break

        self.assertIsInstance(self.event,
                              tooz.coordination.MemberLeftGroup)
        self.assertEqual(member_id_test2,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

        # Stop watching
        self._coord.unwatch_leave_group(self.group_id, self._set_event)
        self.event = None

        # Rejoin and releave group
        client2.join_group(self.group_id).get()
        client2.leave_group(self.group_id).get()
        self._coord.run_watchers()
        self.assertIsNone(self.event)

    def test_watch_join_group_disappear(self):
        if not hasattr(self._coord, '_destroy_group'):
            self.skipTest("This test only works with coordinators"
                          " that have the ability to destroy groups.")

        self._coord.create_group(self.group_id).get()
        self._coord.watch_join_group(self.group_id, self._set_event)
        self._coord.watch_leave_group(self.group_id, self._set_event)

        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        client2.join_group(self.group_id).get()

        while True:
            if self._coord.run_watchers():
                break
        self.assertIsInstance(self.event,
                              tooz.coordination.MemberJoinedGroup)
        self.event = None

        # Force the group to disappear...
        self._coord._destroy_group(self.group_id)

        while True:
            if self._coord.run_watchers():
                break

        self.assertIsInstance(self.event,
                              tooz.coordination.MemberLeftGroup)

    def test_watch_join_group_non_existent(self):
        self.assertRaises(tooz.coordination.GroupNotCreated,
                          self._coord.watch_join_group,
                          self.group_id,
                          lambda: None)
        self.assertEqual(0, len(self._coord._hooks_join_group[self.group_id]))

    def test_watch_join_group_booted_out(self):
        self._coord.create_group(self.group_id).get()
        self._coord.join_group(self.group_id).get()
        self._coord.watch_join_group(self.group_id, self._set_event)
        self._coord.watch_leave_group(self.group_id, self._set_event)

        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        client2.join_group(self.group_id).get()

        while True:
            if self._coord.run_watchers():
                break

        client3 = tooz.coordination.get_coordinator(self.url, self.member_id)
        client3.start()
        client3.leave_group(self.group_id).get()

        # Only works for clients that have access to the groups they are part
        # of, to ensure that after we got booted out by client3 that this
        # client now no longer believes its part of the group.
        if hasattr(self._coord, '_joined_groups'):
            self.assertIn(self.group_id, self._coord._joined_groups)
            self._coord.run_watchers()
            self.assertNotIn(self.group_id, self._coord._joined_groups)

    def test_watch_leave_group_non_existent(self):
        self.assertRaises(tooz.coordination.GroupNotCreated,
                          self._coord.watch_leave_group,
                          self.group_id,
                          lambda: None)
        self.assertEqual(0, len(self._coord._hooks_leave_group[self.group_id]))

    def test_run_for_election(self):
        self._coord.create_group(self.group_id).get()
        self._coord.watch_elected_as_leader(self.group_id, self._set_event)
        self._coord.run_watchers()

        self.assertIsInstance(self.event,
                              tooz.coordination.LeaderElected)
        self.assertEqual(self.member_id,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

    def test_run_for_election_multiple_clients(self):
        self._coord.create_group(self.group_id).get()
        self._coord.watch_elected_as_leader(self.group_id, self._set_event)
        self._coord.run_watchers()

        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        client2.watch_elected_as_leader(self.group_id, self._set_event)
        client2.run_watchers()

        self.assertIsInstance(self.event,
                              tooz.coordination.LeaderElected)
        self.assertEqual(self.member_id,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)
        self.assertEqual(self._coord.get_leader(self.group_id).get(),
                         self.member_id)

        self.event = None

        self._coord.stop()
        client2.run_watchers()

        self.assertIsInstance(self.event,
                              tooz.coordination.LeaderElected)
        self.assertEqual(member_id_test2,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)
        self.assertEqual(client2.get_leader(self.group_id).get(),
                         member_id_test2)

        # Restart the coord because tearDown stops it
        self._coord.start()

    def test_get_leader(self):
        self._coord.create_group(self.group_id).get()

        leader = self._coord.get_leader(self.group_id).get()
        self.assertEqual(leader, None)

        self._coord.join_group(self.group_id).get()

        leader = self._coord.get_leader(self.group_id).get()
        self.assertEqual(leader, None)

        # Let's get elected
        self._coord.watch_elected_as_leader(self.group_id, self._set_event)
        self._coord.run_watchers()

        leader = self._coord.get_leader(self.group_id).get()
        self.assertEqual(leader, self.member_id)

    def test_run_for_election_multiple_clients_stand_down(self):
        self._coord.create_group(self.group_id).get()
        self._coord.watch_elected_as_leader(self.group_id, self._set_event)
        self._coord.run_watchers()

        member_id_test2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id_test2)
        client2.start()
        client2.watch_elected_as_leader(self.group_id, self._set_event)
        client2.run_watchers()

        self.assertIsInstance(self.event,
                              tooz.coordination.LeaderElected)
        self.assertEqual(self.member_id,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

        self.event = None

        self._coord.stand_down_group_leader(self.group_id)
        client2.run_watchers()

        self.assertIsInstance(self.event,
                              tooz.coordination.LeaderElected)
        self.assertEqual(member_id_test2,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

        self.event = None

        client2.stand_down_group_leader(self.group_id)
        self._coord.run_watchers()

        self.assertIsInstance(self.event,
                              tooz.coordination.LeaderElected)
        self.assertEqual(self.member_id,
                         self.event.member_id)
        self.assertEqual(self.group_id,
                         self.event.group_id)

    def test_get_lock(self):
        lock = self._coord.get_lock(self._get_random_uuid())
        self.assertEqual(True, lock.acquire())
        lock.release()
        with lock:
            pass

    def test_get_lock_concurrency_locking_same_lock(self):
        lock = self._coord.get_lock(self._get_random_uuid())

        graceful_ending = threading.Event()

        def thread():
            self.assertTrue(lock.acquire())
            lock.release()
            graceful_ending.set()

        t = threading.Thread(target=thread)
        t.daemon = True
        with lock:
            t.start()
            # Ensure the thread try to get the lock
            time.sleep(.1)
        t.join()
        graceful_ending.wait(.2)
        self.assertTrue(graceful_ending.is_set())

    def _do_test_get_lock_concurrency_locking_two_lock(self, executor,
                                                       use_same_coord):
        name = self._get_random_uuid()
        lock1 = self._coord.get_lock(name)
        with lock1:
            with executor(max_workers=1) as e:
                coord = self._coord if use_same_coord else None
                f = e.submit(try_to_lock_job, name, coord, self.url,
                             self._get_random_uuid())
                self.assertFalse(f.result())

    def test_get_lock_concurrency_locking_two_lock_process(self):
        self._do_test_get_lock_concurrency_locking_two_lock(
            futures.ProcessPoolExecutor, False)

    def test_get_lock_concurrency_locking_two_lock_thread1(self):
        self._do_test_get_lock_concurrency_locking_two_lock(
            futures.ThreadPoolExecutor, False)

    def test_get_lock_concurrency_locking_two_lock_thread2(self):
        self._do_test_get_lock_concurrency_locking_two_lock(
            futures.ThreadPoolExecutor, True)

    def test_get_lock_concurrency_locking2(self):
        # NOTE(sileht): some database based lock can have only
        # one lock per connection, this test ensures acquiring a
        # second lock doesn't release the first one.
        lock1 = self._coord.get_lock(self._get_random_uuid())
        lock2 = self._coord.get_lock(self._get_random_uuid())

        graceful_ending = threading.Event()
        thread_locked = threading.Event()

        def thread():
            with lock2:
                self.assertFalse(lock1.acquire(blocking=False))
                thread_locked.set()
            graceful_ending.set()

        t = threading.Thread(target=thread)
        t.daemon = True

        with lock1:
            t.start()
            thread_locked.wait()
            self.assertTrue(thread_locked.is_set())
        t.join()
        graceful_ending.wait()
        self.assertTrue(graceful_ending.is_set())

    def test_get_lock_twice_locked_twice(self):
        name = self._get_random_uuid()
        lock1 = self._coord.get_lock(name)
        lock2 = self._coord.get_lock(name)
        with lock1:
            self.assertEqual(False, lock2.acquire(blocking=False))

    def test_get_lock_locked_twice(self):
        name = self._get_random_uuid()
        lock = self._coord.get_lock(name)
        with lock:
            self.assertEqual(False, lock.acquire(blocking=False))

    def test_get_multiple_locks_with_same_coord(self):
        name = self._get_random_uuid()
        lock1 = self._coord.get_lock(name)
        lock2 = self._coord.get_lock(name)
        self.assertEqual(True, lock1.acquire())
        self.assertEqual(False, lock2.acquire(blocking=False))
        self.assertEqual(False,
                         self._coord.get_lock(name).acquire(blocking=False))
        lock1.release()

    def test_get_lock_multiple_coords(self):
        member_id2 = self._get_random_uuid()
        client2 = tooz.coordination.get_coordinator(self.url,
                                                    member_id2)
        client2.start()

        lock_name = self._get_random_uuid()
        lock = self._coord.get_lock(lock_name)
        self.assertEqual(True, lock.acquire())

        lock2 = client2.get_lock(lock_name)
        self.assertEqual(False, lock2.acquire(blocking=False))
        lock.release()
        self.assertEqual(True, lock2.acquire(blocking=True))
        lock2.release()

    @staticmethod
    def _get_random_uuid():
        return str(uuid.uuid4()).encode('ascii')


class TestHook(testcase.TestCase):
    def setUp(self):
        super(TestHook, self).setUp()
        self.hooks = tooz.coordination.Hooks()
        self.triggered = False

    def _trigger(self):
        self.triggered = True

    def test_register_hook(self):
        self.assertEqual(self.hooks.run(), [])
        self.assertFalse(self.triggered)
        self.hooks.append(self._trigger)
        self.assertEqual(self.hooks.run(), [None])
        self.assertTrue(self.triggered)

    def test_unregister_hook(self):
        self.hooks.append(self._trigger)
        self.assertEqual(self.hooks.run(), [None])
        self.assertTrue(self.triggered)
        self.triggered = False
        self.hooks.remove(self._trigger)
        self.assertEqual(self.hooks.run(), [])
        self.assertFalse(self.triggered)
