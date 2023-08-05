# Copyright 2014 Hewlett Packard Development Company, L.P.
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
"""
HP3Par SSH Client

.. module: ssh

:Author: Walter A. Boring IV
:Description: This is the SSH Client that is used to make calls to
 the 3PAR where an existing REST API doesn't exist.

"""

import logging
import os
import paramiko
from random import randint
import re

from eventlet import greenthread
from hp3parclient import exceptions


class HP3PARSSHClient(object):
    """This class is used to execute SSH commands on a 3PAR."""

    log_debug = False
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.INFO)

    def __init__(self, ip, login, password,
                 port=22, conn_timeout=None, privatekey=None,
                 **kwargs):
        self.san_ip = ip
        self.san_ssh_port = port
        self.ssh_conn_timeout = conn_timeout
        self.san_login = login
        self.san_password = password
        self.san_private_key = privatekey

        self._create_ssh(**kwargs)

    def _create_ssh(self, **kwargs):
        try:
            ssh = paramiko.SSHClient()

            known_hosts_file = kwargs.get('known_hosts_file', None)
            if known_hosts_file is None:
                ssh.load_system_host_keys()
            else:
                # Make sure we can open the file for appending first.
                # This is needed to create the file when we run CI tests with
                # no existing key file.
                open(known_hosts_file, 'a').close()
                ssh.load_host_keys(known_hosts_file)

            missing_key_policy = kwargs.get('missing_key_policy', None)
            if missing_key_policy is None:
                missing_key_policy = paramiko.AutoAddPolicy()
            elif isinstance(missing_key_policy, basestring):
                # To make it configurable, allow string to be mapped to object.
                if missing_key_policy == paramiko.AutoAddPolicy().__class__.\
                        __name__:
                    missing_key_policy = paramiko.AutoAddPolicy()
                elif missing_key_policy == paramiko.RejectPolicy().__class__.\
                        __name__:
                    missing_key_policy = paramiko.RejectPolicy()
                elif missing_key_policy == paramiko.WarningPolicy().__class__.\
                        __name__:
                    missing_key_policy = paramiko.WarningPolicy()
                else:
                    raise exceptions.SSHException(
                        "Invalid missing_key_policy: %s" % missing_key_policy
                    )

            ssh.set_missing_host_key_policy(missing_key_policy)

            self.ssh = ssh
        except Exception as e:
            msg = "Error connecting via ssh: %s" % e
            self._logger.error(msg)
            raise paramiko.SSHException(msg)

    def _connect(self, ssh):
        if self.san_password:
            ssh.connect(self.san_ip,
                        port=self.san_ssh_port,
                        username=self.san_login,
                        password=self.san_password,
                        timeout=self.ssh_conn_timeout)
        elif self.san_privatekey:
            pkfile = os.path.expanduser(self.san_privatekey)
            privatekey = paramiko.RSAKey.from_private_key_file(pkfile)
            ssh.connect(self.san_ip,
                        port=self.san_ssh_port,
                        username=self.san_login,
                        pkey=privatekey,
                        timeout=self.ssh_conn_timeout)
        else:
            msg = "Specify a password or private_key"
            raise exceptions.SSHException(msg)

    def open(self):
        """Opens a new SSH connection if the transport layer is missing.

        This can be called if an active SSH connection is open already.

        """
        # Create a new SSH connection if the transport layer is missing.
        if self.ssh:
            transport_active = False
            if self.ssh.get_transport():
                transport_active = self.ssh.get_transport().is_active()
            if not transport_active:
                try:
                    self._connect(self.ssh)
                except Exception as e:
                    msg = "Error connecting via ssh: %s" % e
                    self._logger.error(msg)
                    raise paramiko.SSHException(msg)

    def close(self):
        if self.ssh:
            self.ssh.close()

    def set_debug_flag(self, flag):
        """
        This turns on ssh debugging output to console

        :param flag: Set to True to enable debugging output
        :type flag: bool

        """
        if not HP3PARSSHClient.log_debug and flag:
            ch = logging.StreamHandler()
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(ch)
            HP3PARSSHClient.log_debug = True

    def run(self, cmd):
        """Runs a CLI command over SSH, without doing any result parsing."""
        self._logger.debug("SSH CMD = %s " % cmd)

        (stdout, stderr) = self._run_ssh(cmd, False)
        # we have to strip out the input and exit lines
        tmp = stdout.split("\r\n")
        out = tmp[5:len(tmp) - 2]
        self._logger.debug("OUT = %s" % out)
        return out

    def _ssh_execute(self, cmd, check_exit_code=True):
        """We have to do this in order to get CSV output from the CLI command.

        We first have to issue a command to tell the CLI that we want the
        output to be formatted in CSV, then we issue the real command.
        """
        self._logger.debug('Running cmd (SSH): %s', cmd)

        channel = self.ssh.invoke_shell()
        stdin_stream = channel.makefile('wb')
        stdout_stream = channel.makefile('rb')
        stderr_stream = channel.makefile('rb')

        stdin_stream.write('''setclienv csvtable 1
%s
exit
''' % cmd)

        # stdin.write('process_input would go here')
        # stdin.flush()

        # NOTE(justinsb): This seems suspicious...
        # ...other SSH clients have buffering issues with this approach
        stdout = stdout_stream.read()
        stderr = stderr_stream.read()
        stdin_stream.close()
        stdout_stream.close()
        stderr_stream.close()

        exit_status = channel.recv_exit_status()

        # exit_status == -1 if no exit code was returned
        if exit_status != -1:
            self._logger.debug('Result was %s' % exit_status)
            if check_exit_code and exit_status != 0:
                msg = "command %s failed" % cmd
                self._logger.error(msg)
                raise exceptions.ProcessExecutionError(exit_code=exit_status,
                                                       stdout=stdout,
                                                       stderr=stderr,
                                                       cmd=cmd)
        channel.close()
        return (stdout, stderr)

    def _run_ssh(self, cmd_list, check_exit=True, attempts=1):
        self.check_ssh_injection(cmd_list)
        command = ' '. join(cmd_list)

        try:
            total_attempts = attempts
            while attempts > 0:
                attempts -= 1
                try:
                    return self._ssh_execute(command,
                                             check_exit_code=check_exit)
                except Exception as e:
                    self._logger.error(e)
                    greenthread.sleep(randint(20, 500) / 100.0)

            msg = ("SSH Command failed after '%(total_attempts)r' "
                   "attempts : '%(command)s'" %
                   {'total_attempts': total_attempts, 'command': command})
            self._logger.error(msg)
            raise exceptions.SSHException(message=msg)
        except Exception:
            self._logger.error("Error running ssh command: %s" % command)

    def check_ssh_injection(self, cmd_list):
        ssh_injection_pattern = ['`', '$', '|', '||', ';', '&', '&&',
                                 '>', '>>', '<']

        # Check whether injection attacks exist
        for arg in cmd_list:
            arg = arg.strip()

            # Check for matching quotes on the ends
            is_quoted = re.match('^(?P<quote>[\'"])(?P<quoted>.*)(?P=quote)$',
                                 arg)
            if is_quoted:
                # Check for unescaped quotes within the quoted argument
                quoted = is_quoted.group('quoted')
                if quoted:
                    if (re.match('[\'"]', quoted) or
                            re.search('[^\\\\][\'"]', quoted)):
                        raise exceptions.SSHInjectionThreat(
                            command=str(cmd_list))
            else:
                # We only allow spaces within quoted arguments, and that
                # is the only special character allowed within quotes
                if len(arg.split()) > 1:
                    raise exceptions.SSHInjectionThreat(command=str(cmd_list))

            # Second, check whether danger character in command. So the shell
            # special operator must be a single argument.
            for c in ssh_injection_pattern:
                if arg == c:
                    continue

                result = arg.find(c)
                if not result == -1:
                    if result == 0 or not arg[result - 1] == '\\':
                        raise exceptions.SSHInjectionThreat(command=cmd_list)
