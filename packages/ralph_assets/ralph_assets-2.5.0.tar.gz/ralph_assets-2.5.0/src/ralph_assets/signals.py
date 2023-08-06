#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Asset signal module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import django.dispatch

post_transition = django.dispatch.Signal(['user', 'assets', 'transition'])
post_customize_fields = django.dispatch.Signal(['mode'])
