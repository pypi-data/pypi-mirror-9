from collections import Counter
from enum import Enum
from itertools import groupby

__all__ = [
	'CourseType',
	'count', 'rank',
	'rank_courses', 'rank_progress', 'rank_avg_progress'
]


class CourseType(Enum):
	"""
	Identifies whether a course is for speakers and/or learners of a language.
	"""
	SPEAKERS = 1
	LEARNERS = 2
	BOTH     = 3

	@property
	def _tuple(self):
		return {
			1: (0,   ),
			2: (   1,),
			3: (0, 1,),
		}[self.value]


def count(graph, type, key):
	"""
	Sums up a function of course, language for courses of a given type.
	"""
	c = Counter()
	for e in graph.es:
		for i in type._tuple:
			c[graph.vs[e.tuple[i]]['name']] += key(e, graph.vs[e.tuple[i]])
	return c


def rank(counts):
	"""
	Calculates a list of number, list pairs which correspond to the counts
	returned by the count function and languages which match that count, sorted
	in descending order by count.
	"""
	return [
		(key, [lang[0] for lang in group])
		for key, group in groupby(
			sorted(
				counts,
				key = lambda x: x[1],
				reverse = True,
			),
			key = lambda x: x[1],
		)
	]


def rank_courses(graph, type = CourseType.BOTH):
	"""
	Calculates a list of int, list pairs which correspond to the amount of courses
	offered the languages which match that number, sorted in descending order by
	course amount.

	graph:    the Duolingo graph
	type:     CourseType to describe who the courses are for (default BOTH)
	"""
	return rank(count(graph, type, lambda e, v: 1).items())


def rank_progress(graph, type = CourseType.BOTH):
	"""
	Calculates a list of float, list pairs which correspond to the cumulative
	progress of courses offered and the languages which match that number,
	sorted in descending order by course progress.

	graph:    the Duolingo graph
	type:     CourseType to describe who the courses are for (default BOTH)
	"""
	return rank(count(graph, type, lambda e, v: e['progress']).items())


def rank_avg_progress(graph, type = CourseType.BOTH):
	"""
	Calculates a list of float, list pairs which correspond to the average
	progress of courses offered and the languages which match that number,
	sorted in descending order by average progress.
	"""
	courses  = count(graph, type, lambda e, v: 1)
	progress = count(graph, type, lambda e, v: e['progress'])
	return rank((k, progress[k] / courses[k]) for k in courses.keys())
