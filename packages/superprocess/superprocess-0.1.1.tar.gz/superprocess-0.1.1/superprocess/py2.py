import io
import os

# Reopen file with new mode, buffer size etc using io module
def reopen(file, *args, **kwargs):
	fd = os.dup(file.fileno())
	file.close()
	return io.open(fd, *args, **kwargs)

# Popen mixin to improve consistency between Python 2 and 3
class Py2Mixin(object):
	def __init__(self, *args, **kwargs):
		bufsize = kwargs.pop('bufsize', -1)
		universal_newlines = kwargs.pop('universal_newlines', False)

		# initialise process
		super(Py2Mixin, self).__init__(*args, bufsize=bufsize,
			universal_newlines=universal_newlines, **kwargs)

		# reopen standard streams with io module
		if self.stdin and not isinstance(self.stdin, io.IOBase):
			self.stdin = reopen(self.stdin, 'wb', bufsize)
			if universal_newlines:
				self.stdin = io.TextIOWrapper(self.stdin,
					write_through=True, line_buffering=(bufsize == 1))
		if self.stdout and not isinstance(self.stdout, io.IOBase):
			self.stdout = reopen(self.stdout, 'rb', bufsize)
			if universal_newlines:
				self.stdout = io.TextIOWrapper(self.stdout)
		if self.stderr and not isinstance(self.stderr, io.IOBase):
			self.stderr = reopen(self.stderr, 'rb', bufsize)
			if universal_newlines:
				self.stderr = io.TextIOWrapper(self.stderr)
