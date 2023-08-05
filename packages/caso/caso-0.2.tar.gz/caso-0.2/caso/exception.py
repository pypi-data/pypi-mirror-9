# -*- coding: utf-8 -*-

# Copyright 2014 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

import six

from caso import log

LOG = log.getLogger(__name__)


class CasoException(Exception):
    msg_fmt = "An unknown exception occurred."

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if not message:
            try:
                message = self.msg_fmt % kwargs
            except Exception:
                exc_info = sys.exc_info()
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation')
                for name, value in kwargs.iteritems():
                    LOG.error("%s: %s" % (name, value))
                six.reraise(exc_info[0], exc_info[1], exc_info[2])

        super(CasoException, self).__init__(message)


class ClassNotFound(CasoException):
    msg_fmt = "Class %(class_name)s could not be found: %(exception)s."


class LogstashConnectionError(CasoException):
    msg_fmt = ("Cannot send data to logstash %(host)s:%(port)s, "
               "reason: %(exception)s")
