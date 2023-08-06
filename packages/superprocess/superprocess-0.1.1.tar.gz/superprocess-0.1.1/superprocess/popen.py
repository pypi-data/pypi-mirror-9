import subprocess

# Popen mixin that adds a classmethod similar to os.popen()
class OSPopenMixin(object):
	@classmethod
	def popen(Popen, cmd, mode='r', buffering=-1, **kwargs):
		if mode in ('r', 'rt', 'rb'):
			stdin, stdout = None, subprocess.PIPE
		elif mode in ('w', 'wt', 'wb'):
			stdin, stdout = subprocess.PIPE, None
		else:
			raise ValueError('invalid mode %s' % mode)

		p = Popen(cmd, bufsize=buffering, stdin=stdin, stdout=stdout,
			universal_newlines=(mode[-1] != 'b'), **kwargs)

		# wrap file to wait for process on close
		f = p.stdin or p.stdout
		return PopenFile(f, p)

# Helper for popen() - wraps file so that it waits for process when closed
class PopenFile(object):
	def __init__(self, file, process):
		self.file = file
		self.process = process

	def __getattr__(self, name):
		return getattr(self.file, name)

	def __enter__(self):
		return self

	def __exit__(self, *exc):
		self.close()

	def __iter__(self):
		return self

	def __next__(self):
		return next(self.file)

	next = __next__

	def close(self):
		self.file.close()
		returncode = self.process.wait()
		if returncode:
			return returncode
