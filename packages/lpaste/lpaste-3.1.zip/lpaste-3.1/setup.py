import platform
from collections import defaultdict

import setuptools

# add any platform-specific requirements
clipboard_support = defaultdict(lambda: [], {
	'Windows': ['jaraco.windows>=3.1'],
	})[platform.system()]

setup_params = dict(
	name="lpaste",
	use_hg_version=True,
	packages=setuptools.find_packages(),
	entry_points={
		'console_scripts': [
			'lpaste=lpaste.lpaste:main',
		],
	},
	install_requires=[
		'requests',
		'keyring>=0.6',
		'six>=1.4',
	],
	extras_require=dict(
		clipboard=clipboard_support,
	),
	description="Library Paste command-line client",
	license='MIT',
	author="Chris Mulligan",
	author_email="chmullig@gmail.com",
	maintainer='Jason R. Coombs',
	maintainer_email='jaraco@jaraco.com',
	url='https://bitbucket.org/jaraco/lpaste',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
	],
	setup_requires=[
		'hgtools',
	],
)

if __name__ == '__main__':
	setuptools.setup(**setup_params)
