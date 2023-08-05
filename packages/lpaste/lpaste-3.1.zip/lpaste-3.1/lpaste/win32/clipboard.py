from __future__ import print_function, with_statement
import sys
import struct
import io

import jaraco.windows.clipboard as wclip

from lpaste.source import FileSource, CodeSource

def get_image():
	try:
		from PIL import Image
	except ImportError:
		print("PIL not available - image pasting disabled", file=sys.stderr)
		raise
	result = wclip.get_image()
	# construct a header (see http://en.wikipedia.org/wiki/BMP_file_format)
	offset = 54 # 14 byte BMP header + 40 byte DIB header
	header = b'BM'+struct.pack('<LLL', len(result), 0, offset)
	img_stream = io.BytesIO(header+result)
	img = Image.open(img_stream)
	out_stream = io.BytesIO()
	img.save(out_stream, format='jpeg')
	out_stream.seek(0)
	return out_stream, 'image/jpeg', 'image.jpeg'

def try_until_no_exception(*functions):
	for f in functions:
		exceptions = getattr(f, 'exceptions', ())
		try:
			return f()
		except exceptions:
			pass
	raise RuntimeError("No function succeeded")

def do_image():
	return FileSource(*get_image())
def do_html():
	snippet = wclip.get_html()
	return FileSource(io.StringIO(snippet.html), 'text/html',
		'snippet.html')
def do_text():
	code = wclip.get_unicode_text()
	src = CodeSource(code)
	src.check_python()
	return src

def get_source():
	"""
	Return lpaste.Source for the content on the clipboard
	"""
	# try getting an image or html over just text
	do_image.exceptions = (TypeError, ImportError)
	do_html.exceptions = (TypeError,)
	return try_until_no_exception(do_image, do_html, do_text)

set_text = wclip.set_unicode_text
