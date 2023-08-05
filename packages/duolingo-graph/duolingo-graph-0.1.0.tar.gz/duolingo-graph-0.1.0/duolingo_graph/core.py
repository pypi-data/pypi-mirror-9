from igraph import Graph, plot as iplot
from itertools import chain
import requests

__all__ = ['edge_color', 'pull_graph', 'plot']


def edge_color(phase, progress):
	"""
	Determines the colour of an edge of the graph based upon the course's current
	phase and progress, useful for drawing the graph.
	"""
	if phase == 3:
		return 'blue'
	elif phase == 2:
		return 'seagreen'
	else:
		return '#' + ''.join(
			hex(int(mn * (50 - progress) / 50 + mx * progress / 50))[2:]
			for mn, mx in zip((0xFF, 0x40, 0x40), (0xbf, 0xbf, 0x40))
		)


def pull_graph(phase = 1, progress = 0):
	"""
	Connects to the Incubator API and generates an igraph Graph of the languages
	learned, where edges point from languages kown to languages learned.

	phase:    minimum phase    of nodes on the graph
	progress: minimum progress of nodes on the graph
	"""
	json = requests.get(
		'http://incubator.duolingo.com/api/1/courses/list',
		headers = {'Connection': 'Close'}
	).json()
	return Graph.TupleList((
		(
			json['languages'][d['from_language_id']]['name'],
			json['languages'][d['learning_language_id']]['name'],
			edge_color(d['phase'], d['progress']),
			d['phase'],
			d['progress'],
		)
		for d in json['directions']
		if  d['phase']    >= phase
		and d['progress'] >= progress
	), directed = True, edge_attrs = ('color', 'phase', 'progress'))


def plot(graph, layout = 'lgl'):
	"""
	Plots a Duolingo graph, using a given igraph layout.
	"""
	iplot(graph,
		layout = graph.layout('fr'),
		vertex_label = graph.vs['name'],
		edge_width = 1.25,
		edge_arrow_width = 1,
		vertex_size = 10,
		vertex_label_dist = 2,
		vertex_label_size = 16,
		font_family = 'Inconsolata',
		bbox = (800, 800),
		margin = 50,
	)
