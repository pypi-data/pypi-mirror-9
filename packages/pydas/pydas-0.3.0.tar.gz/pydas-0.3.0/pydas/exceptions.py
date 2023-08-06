#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#
# Library: pydas
#
# Copyright 2010 Kitware, Inc., 28 Corporate Dr., Clifton Park, NY 12065, USA.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

"""Modules for defining exceptions in pydas."""


class PydasException(Exception):
    """Base class for exception to throw within pydas."""

    def __init__(self, value):
        """
        Override the constructor to support a basic message.

        :param value: message
        :type value: string
        """
        super(PydasException, self).__init__()
        self.value = value
        self.method = None
        self.code = None

    def __str__(self):
        """
        Override the string method.

        :returns: string representation of the message
        :rtype: string
        """
        return repr(self.value)
