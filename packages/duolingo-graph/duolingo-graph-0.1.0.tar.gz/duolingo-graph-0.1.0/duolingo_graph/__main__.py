from .core    import *
from .numbers import *
import click


__all__ = ['main']


class CLIData(object):
	__slots__ = ('graph', 'n', 'kind')


_helps = {
	'phase': "don't include courses below given phase",
	'progress': "don't include courses below given progress",
	'n': "limit number of courses to show (0 for no limit)",
	'learners': "only rank languages by courses for learners",
	'speakers': "only rank languages by courses for speakers",
	'all': "rank by all courses featuring a language (default)",
}

@click.group()
@click.option('--phase',    '-l', default = 1, type = click.INT,
	help = _helps['phase'])
@click.option('--progress', '-p', default = 0, type = click.FLOAT,
	help = _helps['progress'])
@click.pass_context
def cli(ctx, phase, progress):
	"""Graph the courses on Duolingo."""
	def load_graph():
		click.echo('Connecting to Duolingo Incubator API...', nl = False, err = True)
		graph = pull_graph(
			phase    = phase,
			progress = progress,
		)
		click.echo('done.', err = True)
		return graph
	ctx.obj.graph = load_graph


@cli.group(name = 'rank-by')
@click.option('-n', default = 0, type = click.IntRange(0, None),
	help = _helps['n'])
@click.option('--learners', '-L', 'kind', flag_value = CourseType.LEARNERS,
	help = _helps['learners'])
@click.option('--speakers', '-S', 'kind', flag_value = CourseType.SPEAKERS,
	help = _helps['speakers'])
@click.option('--all',            'kind', flag_value = CourseType.BOTH,
	help = _helps['all'], default = True)
@click.pass_context
def rank_by(ctx, n, kind):
	"""Rank languages by some criteria."""
	ctx.obj.n = n
	ctx.obj.kind = kind


def print_ranks(ranks, label, labels, fmt):
	"""
	Beautifully prints a list that's returned from either rank_courses or
	rank_progress.
	"""
	if len(ranks) == 0: return
	width = max(len(('{:' + fmt + '}').format(amt)) for amt, _ in ranks)
	for amt, langs in ranks:
		print(('  {:' + str(width) + fmt + '}{} {}').format(
			amt,
			labels if float(amt) > 1 else label,
			(',\n' + ' ' * (2 + width + len(labels) + 1)).join(langs)
		))


@rank_by.command()
@click.pass_context
def courses(ctx):
	"""Rank by number of courses."""
	ranks = rank_courses(ctx.obj.graph(), ctx.obj.kind)
	print_ranks(
		ranks if ctx.obj.n == 0 else ranks[:ctx.obj.n],
		' course: ', ' courses:', 'd',
	)


@rank_by.command(name = 'total-progress')
@click.pass_context
def total_progress(ctx):
	"""Rank by total course progress."""
	ranks = rank_progress(ctx.obj.graph(), ctx.obj.kind)
	print_ranks(
		ranks if ctx.obj.n == 0 else ranks[:ctx.obj.n],
		'% progress:', '% progress:', '.4f',
	)


@rank_by.command(name = 'avg-progress')
@click.pass_context
def avg_progress(ctx):
	"""Rank by average course progress."""
	ranks = rank_avg_progress(ctx.obj.graph(), ctx.obj.kind)
	print_ranks(
		ranks if ctx.obj.n == 0 else ranks[:ctx.obj.n],
		'% progress:', '% progress:', '.4f',
	)


@cli.command()
@click.pass_context
def display(ctx):
	"""Visually graph the courses."""
	plot(ctx.obj.graph())


def main():
	"""Main function for duolingo_graph"""
	cli(obj = CLIData())

if __name__ == '__main__':
	main()
