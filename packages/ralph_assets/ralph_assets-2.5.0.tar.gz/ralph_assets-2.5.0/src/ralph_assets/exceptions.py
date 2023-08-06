#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class PostTransitionException(Exception):
    """General exception to be thrown in *post_transition* signal receivers.
    Exception message is used to inform user."""
