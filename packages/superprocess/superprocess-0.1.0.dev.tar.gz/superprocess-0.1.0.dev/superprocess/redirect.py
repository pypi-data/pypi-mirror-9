from subprocess import STDOUT

STDERR = -4

# Popen mixin to extend support for redirecting streams
class RedirectMixin(object):
	def __init__(self, *args, **kwargs):
		stdout = kwargs.pop('stdout', None)
		stderr = kwargs.pop('stderr', None)

		# stdout=STDERR: combine streams into stdout initially
		redir_stdout = (stdout == STDERR)
		if redir_stdout:
			stdout, stderr = stderr, STDOUT

		# initialise process
		super(RedirectMixin, self).__init__(
			*args, stdout=stdout, stderr=stderr, **kwargs)

		# stdout=STDERR: move output to stderr
		if redir_stdout:
			self.stdout, self.stderr = None, self.stdout
