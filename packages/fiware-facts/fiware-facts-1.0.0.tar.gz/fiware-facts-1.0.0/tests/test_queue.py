# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefonica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#

from unittest import TestCase
from facts.queue import myqueue
from mockito import *
import pika

__author__ = 'fla'

""" Class to test the interaction with rabbitmq
"""


class TestQueue(TestCase):
    pass

    def testConnectionNone(self):
        queue = myqueue()

        queue.connection = None

        expectedvalue = "AMQP connection not properly created..."

        try:
            queue.publish_message("tenantid", "hola")
        except (Exception), err:
            self.assertEqual(expectedvalue, err.message)

    def testChannelNone(self):
        queue = myqueue()

        queue.channel = None

        expectedvalue = "AMQP channel not properly created..."

        try:
            queue.publish_message("tenantid", "hola")
        except (Exception), err:
            self.assertEqual(expectedvalue, err.message)
