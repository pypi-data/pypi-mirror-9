########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

__author__ = 'elip'


class NonRecoverableError(Exception):
    """
    An error raised by plugins to denote that no retry should be attempted by
    by the executing workflow engine.
    """
    pass


class RecoverableError(Exception):
    """
    An error raised by plugins to explicitly denote that this is a recoverable
    error (note that this is the default behavior). It is possible specifying
    how many seconds should pass before a retry is attempted thus overriding
    the bootstrap context configuration parameter:
    ``cloudify.workflows.retry_interval``

    :param retry_after: How many seconds should the workflow engine wait
                        before re-executing the task the raised this
                        exception. (only applies when the workflow engine
                        decides that this task should be retried)
    """

    def __init__(self, message=None, retry_after=None):
        message = message or ''
        if retry_after is not None:
            message = '{0} [retry_after={1}]'.format(message, retry_after)
        super(RecoverableError, self).__init__(message)
        self.retry_after = retry_after


class HttpException(NonRecoverableError):
    """
    Wraps HTTP based exceptions that may be raised.

    :param url: The url the request was made to.
    :param code: The response status code.
    :param message: The underlying reason for the error.

    """

    def __init__(self, url, code, message):
        self.url = url
        self.code = code
        self.message = message
        super(HttpException, self).__init__(str(self))

    def __str__(self):
        return "{0} ({1}) : {2}".format(self.code, self.url, self.message)


class CommandExecutionException(Exception):
    """
    Indicates a failure to execute a command.

    :param command: The command executed
    :param error: process stderr output
    :param output: process stdout output
    :param code: process exit code
    """

    def __init__(self, command, error, output, code):
        self.command = command
        self.error = error
        self.code = code
        self.output = output
        Exception.__init__(self, self.__str__())

    def __str__(self):
        return "Failed executing command: {0}\ncode: " \
               "{1}\nerror: {2}\nmessage: {3}"\
               .format(self.command, self.code, self.error, self.output)


class TimeoutException(Exception):
    """Indicates some kind of timeout happened."""
    def __init__(self, *args):
        Exception.__init__(self, args)


class ProcessExecutionError(RuntimeError):
    """Raised by the workflow engine when workflow execution fails."""

    def __init__(self, message, error_type=None, traceback=None):
        super(Exception, self).__init__(message)
        self.error_type = error_type
        self.traceback = traceback

    def __str__(self):
        if self.error_type:
            return '{0}: {1}'.format(self.error_type, self.message)
        return self.message
