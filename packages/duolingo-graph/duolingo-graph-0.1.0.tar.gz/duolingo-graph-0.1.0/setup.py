from distutils.core import setup

setup(
	name = 'duolingo-graph',
	version = '0.1.0',
	description = 'Utilities to graph the courses on Duolingo.',
	author = 'Claire Charron',
	author_email = 'claire@undeterminant.net',
	packages = ['duolingo_graph'],
	scripts = ['scripts/duolingo-graph'],
	url = 'https://github.com/Undeterminant/duolingo-graph',
	license = 'CC0'
)
