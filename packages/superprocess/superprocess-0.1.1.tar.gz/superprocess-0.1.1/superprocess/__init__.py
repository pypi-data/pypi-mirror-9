import subprocess

from superprocess import base, popen, py2, redirect, remote

__all__ = ['Popen', 'PIPE', 'STDOUT', 'STDERR', 'call',
	'check_call', 'check_output', 'CalledProcessError']

PIPE = subprocess.PIPE
STDOUT = subprocess.PIPE
STDERR = redirect.STDERR
CalledProcessError = subprocess.CalledProcessError

class Popen(
		popen.OSPopenMixin,
		redirect.RedirectMixin,
		remote.RemoteShellMixin,
		base.PopenMixin,
		py2.Py2Mixin,
		subprocess.Popen):
	pass

call = Popen.call
check_call = Popen.check_call
check_output = Popen.check_output
popen = Popen.popen
