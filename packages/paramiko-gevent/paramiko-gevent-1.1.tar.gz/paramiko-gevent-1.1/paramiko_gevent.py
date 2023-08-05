# Paramiko + gevent
# File: paramiko_gevent.py
# Desc: a *tiny* wrapper around Paramiko's SSHClient to support running in parallel via gevent

from gevent import sleep, monkey
monkey.patch_all()

from paramiko import SSHClient as ParamikoSSHClient


class SSHClient(ParamikoSSHClient):
    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False):
        '''This is basically an exact copy of the original exec_command + a while loop.'''
        # Get & prep a new session (paramiko.channel.Channel)
        channel = self._transport.open_session()
        channel.settimeout(timeout)

        if get_pty:
            channel.get_pty()

        # Prep stdout & stderr as file-like objects
        stdout = channel.makefile('r', bufsize)
        stderr = channel.makefile_stderr('r', bufsize)

        # Execute the command on the remote host
        channel.exec_command(command)

        # This is the key to gevent compatability, Paramiko's SSHClient returns
        # stdout & stderr, but they block when read. Here we wait until the
        # data is ready or the channel has closed.
        while not (channel.recv_ready() or channel.recv_stderr_ready() or channel.closed):
            sleep(0.2)

        return stdout, stderr
