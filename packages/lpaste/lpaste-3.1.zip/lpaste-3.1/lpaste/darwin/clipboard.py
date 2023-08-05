import os
from lpaste.source import CodeSource

# from pyperclip (http://coffeeghost.net/2010/10/09/pyperclip-a-cross-platform-clipboard-module-for-python)

def macSetClipboard(text):
	outf = os.popen('pbcopy', 'w')
	outf.write(text)
	outf.close()

def macGetClipboard():
	outf = os.popen('pbpaste', 'r')
	content = outf.read()
	outf.close()
	return content

def get_source():
	code = macGetClipboard()
	src = CodeSource(code=code)
	src.check_python()
	return src

def set_text(text):
	macSetClipboard(text.encode('utf-8'))
