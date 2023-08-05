import abc
import mimetypes
import collections

# add mimetypes not present in Python
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('application/json', '.json')

# a "file" in requests is a tuple of name, stream, content_type
RequestsFile = collections.namedtuple('RequestsFile',
	'filename stream content_type')

class Source(object):
	@abc.abstractmethod
	def apply(self, data):
		"Apply this source to the data and return any files"

class CodeSource(Source):
	def __init__(self, code):
		self.code = code

	def apply(self, data):
		data['code'] = self.code

	def check_python(self):
		try:
			# see if the code can compile as Python
			compile(self.code, 'pasted_code.py', 'exec')
			self.format = 'python'
		except:
			pass # use default format


class FileSource(Source):
	def __init__(self, stream, content_type=None, filename=None):
		self.stream = stream
		self.content_type = content_type
		self.filename = filename

	def apply(self, data):
		content_type = self.content_type
		if self.filename and not content_type:
			content_type, _ = mimetypes.guess_type(self.filename)
		if not content_type:
			content_type = 'application/octet-stream'
		return {
			'file': RequestsFile(self.filename, self.stream, content_type),
		}
