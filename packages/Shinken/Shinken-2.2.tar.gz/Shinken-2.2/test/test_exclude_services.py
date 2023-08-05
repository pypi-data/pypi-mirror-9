#!/usr/bin/env python
# Copyright (C) 2009-2014:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

#
# This file is used to test object properties overriding.
#

import re
from shinken_test import unittest, ShinkenTest


class TestPropertyOverride(ShinkenTest):

    def setUp(self):
        self.setup_with_file('etc/shinken_exclude_services.cfg')

    def test_exclude_services(self):
        hst1 = self.sched.hosts.find_by_name("test_host_01")
        hst2 = self.sched.hosts.find_by_name("test_host_02")

        self.assertEqual([], hst1.service_excludes)
        self.assertEqual(["srv-svc11", "srv-svc21", "proc proc1"], hst2.service_excludes)

        # All services should exist for test_host_01
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_01", "srv-svc11")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_01", "srv-svc12")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_01", "srv-svc21")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_01", "srv-svc22")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_01", "proc proc1")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_01", "proc proc2")
        self.assertIsNot(svc, None)

        # Half the services only should exist for test_host_02
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_02", "srv-svc11")
        self.assertIs(None, svc)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_02", "srv-svc12")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_02", "srv-svc21")
        self.assertIs(None, svc)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_02", "srv-svc22")
        self.assertIsNot(svc, None)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_02", "proc proc1")
        self.assertIs(None, svc)
        svc = self.sched.services.find_srv_by_name_and_hostname("test_host_02", "proc proc2")
        self.assertIsNot(svc, None)



if __name__ == '__main__':
    unittest.main()
