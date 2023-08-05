parallel-ssh
============

Library for running asynchronous parallel SSH commands over many hosts.

parallel-ssh uses asychronous network requests - there is *no* multi-threading or multi-processing used.

This is a *requirement* for commands on many (hundreds/thousands/hundreds of thousands) of hosts which would grind a system to a halt simply by having so many processes/threads all wanting to execute if done with multi-threading/processing.

.. image:: https://travis-ci.org/pkittenis/parallel-ssh.svg?branch=master
  :target: https://travis-ci.org/pkittenis/parallel-ssh
.. image:: https://coveralls.io/repos/pkittenis/parallel-ssh/badge.png?branch=master
  :target: https://coveralls.io/r/pkittenis/parallel-ssh?branch=master
.. image:: https://pypip.in/download/parallel-ssh/badge.png
  :target: https://pypi.python.org/pypi/parallel-ssh
  :alt: downloads
.. image:: https://readthedocs.org/projects/parallel-ssh/badge/?version=latest
  :target: http://parallel-ssh.readthedocs.org/en/latest/
  :alt: Latest documentation

.. _`read the docs`: http://parallel-ssh.readthedocs.org/en/latest/

************
Installation
************

::

   $ pip install parallel-ssh

*************
Usage Example
*************

See documentation on `read the docs`_ for more complete examples.

Run `ls` on two remote hosts in parallel.

>>> from pssh import ParallelSSHClient
>>> hosts = ['myhost1', 'myhost2']
>>> client = ParallelSSHClient(hosts)
>>> output = client.run_command('ls -ltrh /tmp/', sudo=True)
>>> print output
{'myhost1': {'exit_code': 0, 'stdout': <generator>, 'stderr': <generator>, 'channel': <channel>, 'cmd' : <greenlet>},
 'myhost2': {'exit_code': 0, 'stdout': <generator>, 'stderr': <generator>, 'channel': <channel>, 'cmd' : <greenlet>}}

Stdout and stderr buffers are available in output. Iterating on them can be used to get output as it becomes available.

>>> for host in output:
>>>     for line in output[host]['stdout']:
>>>         print "Host %s - output: %s" % (host, line)
Host myhost1 - output: drwxr-xr-x  6 xxx xxx 4.0K Jan  1 00:00 xxx
Host myhost2 - output: drwxr-xr-x  6 xxx xxx 4.0K Jan  1 00:00 xxx

Joining on the connection pool can be used to block and wait for all parallel commands to finish if reading stdout/stderr is not required.

>>> client.pool.join()


**************************
Frequently asked questions
**************************

:Q:
   Why should I use this module and not, for example, `fabric <https://github.com/fabric/fabric>`_?

:A:
   Fabric is a port of `Capistrano <https://github.com/capistrano/capistrano>`_ from ruby to python. Its design goals are to provide a faithful port of capistrano with its `tasks` and `roles` to python with interactive command line being the intended usage. Its use as a library is non-standard and in `many <https://github.com/fabric/fabric/issues/521>`_ `cases <https://github.com/fabric/fabric/pull/674>`_ `just <https://github.com/fabric/fabric/pull/1215>`_ `plain <https://github.com/fabric/fabric/issues/762>`_ `broken <https://github.com/fabric/fabric/issues/1068>`_.
   
   Furthermore, its parallel commands use a combination of both threads and processes with extremely high CPU usage and system load while running. Fabric currently stands at over 6,000 lines of code, majority of which is untested, particularly if used as a library as opposed to less than 700 lines of code mostly consisting of documentation strings currently in `ParallelSSH` with over 80% code test coverage.
   
   ParallelSSH's design goals and motivation are to provide a *library* for running *asynchronous* SSH commands in parallel with **no** load induced on the system by doing so with the intended usage being completely programmatic and non-interactive - Fabric provides none of these goals.

:Q:
 Are SSH agents used?

:A:
 All available keys in a running SSH agent in addition to SSH keys in the user's home directory, `~/.ssh/id_dsa`, `~/.ssh/id_rsa` et al are automatically used by ParallelSSH.

:Q:
  Can ParallelSSH forward my SSH agent?

:A:
  SSH agent forwarding, what `ssh -A` does on the command line, is supported and enabled by default. Creating an object as `ParallelSSHClient(forward_ssh_agent=False)` will disable that behaviour.

:Q:
  Is tunneling/proxying supported?

:A:
  ParallelSSH natively supports tunelling through an intermediate SSH server. Connecting to a remote host is accomplished via an SSH tunnel using the SSH's protocol direct TCP tunneling feature, using local port forwarding. This is done natively in python and tunnel connections are asynchronous like all other connections in the ParallelSSH library. For example, client -> proxy SSH server -> remote SSH destination.

  Use the `proxy_host` and `proxy_port` parameters to configure your proxy.

  >>> client = ParallelSSHClient(hosts, proxy_host='my_ssh_proxy_host')
  
  Note that while connections from the ParallelSSH client to the tunnel host are asynchronous, connections from the tunnel host to the remote destination(s) may not be, depending on the SSH server implementation. If the SSH server uses threading to implement its tunelling and that server is used to tunnel to a large number of remote destinations system load on the tunnel server will increase linearly according to number of remote hosts.

:Q:
  Is there a way to programmatically provide an SSH key?

:A:
  Yes, use the `pkey` parameter of the `ParallelSSHClient class <http://parallel-ssh.readthedocs.org/en/latest/#pssh.ParallelSSHClient>`_. For example:

  >>> import paramiko
  >>> client_key = paramiko.RSAKey.from_private_key_file('user.key')
  >>> client = ParallelSSHClient(['myhost1', 'myhost2'], pkey=client_key)

:Q:
   Is there a user's group for feedback and discussion about ParallelSSH?
:A:
   There is a public `ParallelSSH Google group <https://groups.google.com/forum/#!forum/parallelssh>`_ setup for this purpose - both posting and viewing are open to the public.

********
SFTP/SCP
********

SFTP is supported (SCP version 2) natively, no `scp` command required.

For example to copy a local file to remote hosts in parallel

>>> from pssh import ParallelSSHClient
>>> hosts = ['myhost1', 'myhost2']
>>> client = ParallelSSHClient(hosts)
>>> client.copy_file('../test', 'test_dir/test')
>>> client.pool.join()
Copied local file ../test to remote destination myhost1:test_dir/test
Copied local file ../test to remote destination myhost2:test_dir/test
