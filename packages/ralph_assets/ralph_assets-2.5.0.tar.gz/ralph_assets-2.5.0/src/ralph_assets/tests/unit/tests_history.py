# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase

from ralph_assets.tests.utils.assets import DeviceInfoFactory


class HistoryTestCase(TestCase):
    def test_change_device_info(self):
        device_info = DeviceInfoFactory()
        old_length = len(device_info.get_history())
        device_info.position += 1
        device_info.save()
        self.assertEqual(old_length + 1, len(device_info.get_history()))
