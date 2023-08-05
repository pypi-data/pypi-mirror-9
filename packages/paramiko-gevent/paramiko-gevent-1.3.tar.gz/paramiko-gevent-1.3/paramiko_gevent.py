# Paramiko + gevent
# File: paramiko_gevent.py
# Desc: a *tiny* wrapper around Paramiko's SSHClient to support running in parallel via gevent

from gevent import sleep, monkey
monkey.patch_all()

from paramiko import SSHClient as ParamikoSSHClient


class SSHClient(ParamikoSSHClient):
    def exec_command(self, *args, **kwargs):
        # Exec the original command
        stdin, stdout, stderr = super(SSHClient, self).exec_command(*args, **kwargs)
        channel = stdout.channel

        # This is the key to gevent compatability, Paramiko's SSHClient returns
        # stdout & stderr, but they block when read. Here we wait until the
        # data is ready or the channel has closed.
        while not (channel.recv_ready() or channel.recv_stderr_ready() or channel.closed):
            sleep(0.2)

        return stdin, stdout, stderr
