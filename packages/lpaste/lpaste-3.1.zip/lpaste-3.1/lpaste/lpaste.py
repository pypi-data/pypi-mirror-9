from __future__ import absolute_import, print_function

import os
import sys
import re
import getpass
import importlib
import argparse
import logging
import pdb
import socket
import functools

from six.moves import http_client

import pkg_resources
import webbrowser
import requests

try:
	import keyring
except ImportError:
	keyring = None

from .source import CodeSource, FileSource

try:
	mod_name = 'lpaste.%s.clipboard' % sys.platform
	clipb = importlib.import_module(mod_name)
except ImportError:
	clipb = None

version = pkg_resources.require('lpaste')[0].version
session = requests.Session()
log = logging.getLogger(__name__)

BASE_HEADERS = {
	'User-Agent': 'lpaste ({version}) Python ({sys.version})'.format(**locals())
}

def log_level(level_str):
	return getattr(logging, level_str.upper())

def _resolve_url():
    """
    if 'paste' resolves in this environment, use the hostname for which
    that name resolves.
    Override with 'LIBRARYPASTE_URL'
    """
    try:
        name, aliaslist, addresslist = socket.gethostbyname_ex('paste')
    except socket.gaierror:
    	# jaraco generously hosts paste for the world
        name = 'paste.jaraco.com'
    name = _patch_heroku(name, aliaslist)
    fallback = 'https://{name}/'.format(name=name)
    return os.environ.get('LIBRARYPASTE_URL', fallback)

def _patch_heroku(name, aliases):
	"""
	Heroku will resolve its host to a name which fails SSL validation. Find a
	preferable name from the aliases.
	"""
	if name.endswith('.route.herokuapp.com'):
		matches = filter(re.compile(r'[^.]*\.herokuapp\.com').match, aliases)
		name = next(matches, name)
	return name

def get_options():
	default_url = _resolve_url()
	default_user = os.environ.get('LIBRARYPASTE_USER', getpass.getuser())

	description = "version {version}".format(**globals())

	parser = argparse.ArgumentParser(description=description)

	parser.add_argument('-s', '--site', dest='site',
		default=default_url,
		help="URL for the library paste site to use. By default: %s" %
		default_url)
	parser.add_argument('-t', '--format', dest='format', default='_',
		help="Which syntax code highlighter would you like to use? "
		"Defaults to plain text.")
	parser.add_argument('-u', '--username', dest='username',
		default=default_user, help="Username to paste as, attempts to "
		"use system account name if none specified.")
	parser.add_argument('-l', '--longurl', dest='longurl',
		action="store_true", default=False,
		help="Use a long url instead of the default short")
	parser.add_argument('-a', '--attach', dest='attach',
		action="store_true", default=False,
		help="Upload the file as an attachment instead of as code/text")
	parser.add_argument('-b', '--browser', dest='browser',
		action="store_true", default=False,
		help="Open your paste in a new browser window after it's "
		"uploaded")
	parser.add_argument('-c', '--clipboard',
		action="store_true", default=False,
		help="Get the input from the clipboard")
	parser.add_argument('--auth-username', default=default_user,
		help="The username to use when HTTP auth is required",)
	parser.add_argument('--log-level', default=logging.WARNING,
		type=log_level)
	parser.add_argument('--debug', default=False, action='store_true',
		help="Drop into a PDB prompt if the POST fails.")
	parser.add_argument('file', nargs='?',
		help="If file is not supplied, stdin will be used.")
	if not keyring:
		parser.add_argument('--auth-password',
			help="The password to use when HTTP auth is required",)
	options = parser.parse_args()
	if options.file and options.clipboard:
		parser.error("Either supply a file or --clipboard, but not both")
	if options.clipboard:
		if not clipb:
			parser.error("Clipboard support not available - you must "
				"supply a file")
		source = clipb.get_source()
	else:
		use_stdin = options.file in (None, '-')
		stream = open(options.file, 'rb') if not use_stdin else sys.stdin
		filename = os.path.basename(options.file) if not use_stdin else None
		if options.attach:
			source = FileSource(stream, filename=filename)
		else:
			source = CodeSource(stream.read())

	options.source = source
	if hasattr(source, 'format'):
		options.format = source.format
	return options


def parse_auth_realm(resp):
	"""
	From a 401 response, parse out the realm for basic auth.
	"""
	header = resp.headers['www-authenticate']
	mode, _sep, dict = header.partition(' ')
	assert mode.lower() == 'basic'
	return requests.utils.parse_dict_header(dict)['realm']

def get_auth(options, realm):
	username = options.auth_username
	if keyring:
		return username, keyring.get_password(realm, username)
	password = options.auth_password or getpass.getpass()
	return username, password

def configure_logging(level):
	logging.basicConfig(level=level)

	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(level)
	requests_log.propagate = True

	# enable debugging at http.client level (requests->urllib3->http.client)
	http_client.HTTPConnection.debuglevel = level <= logging.DEBUG

def detect_auth(url, resolver):
	"""
	Load the root URL to determine if auth is required. `resolver` should
	resolve a realm to an auth parameter.

	Return an auth parameter suitable for a request parameter.
	"""
	resp = session.get(url)
	if resp.status_code != 401:
		return None
	realm = parse_auth_realm(resp)
	return resolver(realm)

def main():

	options = get_options()
	configure_logging(options.log_level)

	log.info("Using {site}".format(**vars(options)))

	paste_url = options.site
	data = {'nick': options.username, 'fmt': options.format, }
	if not options.longurl:
		data['makeshort'] = 'True'
	files = options.source.apply(data)
	headers = dict(BASE_HEADERS)

	resolver = functools.partial(get_auth, options)
	auth = detect_auth(paste_url, resolver)
	resp = session.post(paste_url, headers=headers, data=data, files=files,
		auth=auth)
	if not resp.ok and options.debug:
		pdb.set_trace()
	resp.raise_for_status()
	url = resp.url
	if clipb: clipb.set_text(url)
	print('Paste URL:', url)
	if options.browser:
		print("Now opening browser...")
		webbrowser.open(url)

def get_realm(authenticate_header):
	pattern = re.compile('\w+ realm="(?P<realm>.*)"')
	res = pattern.match(authenticate_header)
	return res.groupdict()['realm']

if __name__ == '__main__':
	main()
