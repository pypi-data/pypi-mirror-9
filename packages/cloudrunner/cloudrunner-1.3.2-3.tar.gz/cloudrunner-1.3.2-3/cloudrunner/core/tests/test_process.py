#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 CloudRunner.IO
# All Rights Reserved.
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

import socket
import os
import pwd
from mock import patch, MagicMock

import cloudrunner
from cloudrunner.tests import base
from cloudrunner.core.platform.nix import PopenWrapper

LOCAL_USER = pwd.getpwuid(os.getuid())[0]


class TestProcess(base.BaseTestCase):

    @patch('os.name', 'posix')
    def test_run_process_bash(self):
        from cloudrunner.core.process import Processor
        proc = Processor(os.environ['USER'])
        replies = proc.run("""#! /usr/bin/bash
echo 1

export KEY2=$(python -c "import socket; print socket.gethostname()")
echo 2

__exit 3""", 'bash', {'KEY1': 'SOME VALUE'})

        pipe = next(replies)
        host = socket.gethostname()
        self.assertType(pipe, PopenWrapper)

        self.assertEqual(pipe.stdout.readline(), '1\n')
        self.assertEqual(pipe.stdout.readline(), '2\n')
        self.assertEqual(next(replies), [LOCAL_USER, 3, '', '',
                                         {'KEY2': host}])

        self.assertIsNotNone(pipe.poll())
        self.assertRaises(StopIteration, next, replies)

    @patch('os.name', 'posix')
    def test_run_process_python(self):
        from cloudrunner.core.process import Processor
        proc = Processor(os.environ['USER'])
        replies = proc.run("""#! /usr/bin/python
import os
import time
import socket

print 1
print os.environ['PATH']
os.environ['KEY2'] = socket.gethostname()
print 2

__exit(3)""", 'python', {'KEY1': 'SOME VALUE'})
        pipe = next(replies)
        self.assertType(pipe, PopenWrapper)
        self.assertEqual(pipe.stdout.readline(), '1\n')
        self.assertEqual(pipe.stdout.readline(
        ), '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n')
        self.assertEqual(pipe.stdout.readline(), '2\n')
        self.assertEqual(next(replies), [LOCAL_USER, 3, '', '',
                                         {'KEY2': socket.gethostname()}])
        self.assertIsNotNone(pipe.poll())
        self.assertRaises(StopIteration, next, replies)

    win32security, win32con, win32api, ntsecuritycon = \
        MagicMock(), MagicMock(), MagicMock(), MagicMock()

    @patch.dict('sys.modules', win32security=win32security, win32con=win32con,
                win32api=win32api, ntsecuritycon=ntsecuritycon)
    @patch('os.name', 'nt')
    def test_run_process_python_nt(self):
        reload(cloudrunner.core.process)
        from cloudrunner.core.process import Processor
        proc = Processor(os.environ['USER'])

        self.assertEqual(
            proc.executor.get_path(),
            '%SystemRoot%\\system32;%SystemRoot%;%SystemRoot%\\System32\\Wbem;'
            '%SYSTEMROOT%\\System32\\WindowsPowerShell\\v1.0\\')
