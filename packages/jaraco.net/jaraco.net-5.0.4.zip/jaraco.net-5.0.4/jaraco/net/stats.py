import re
import datetime
import itertools
import argparse
import importlib
import textwrap

import six

from more_itertools import recipes
import dateutil.parser
from svg.charts import time_series

class PingResult(object):
	def __init__(self, text):
		pattern = re.compile('time: (?P<time>.*), host: (?P<host>.*), '
			'res: (?P<result>.*)\n')
		res = pattern.match(text).groupdict()
		res['time'] = dateutil.parser.parse(res['time'])
		self.__dict__.update(res)
		if self.result == 'None':
			self.result = None

	@property
	def date(self):
		return self.time.date()

	@property
	def latency(self):
		if not self:
			return
		hours, minutes, seconds = self.result.split(':')
		return datetime.timedelta(
			hours=float(hours),
			minutes=float(minutes),
			seconds=float(seconds),
		)

	@property
	def type(self):
		if self.result is None:
			return 'loss'
		if 'transmission failure' in self.result:
			return 'error'
		if 'Network is unreachable' in self.result:
			return 'environment'
		return 'success'

	def success(self):
		return self.type == 'success'

	__bool__ = __nonzero__ = success

class Reader(object):
	def __init__(self, filename):
		self.filename = filename
		self.file = open(filename)

	def get_stats(self):
		return six.moves.map(PingResult, self.file)

	def __del__(self):
		self.file.close()

def single_day(stats, day):
	"skip day-1 days then return only results from the next day"
	days_seen = set()
	for ping in stats:
		days_seen.add(ping.date)
		if len(days_seen) == day:
			yield ping
		if len(days_seen) > day:
			return

def windows(seq, n=2):
	"""
	Return a sliding window (of width n) over data from the iterable
	s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
	"""
	it = iter(seq)
	result = tuple(itertools.islice(it, n))
	if len(result) == n:
		yield result
	for elem in it:
		result = result[1:] + (elem,)
		yield result

def get_loss_stats(window):
	total = len(window)
	loss = len([ping for ping in window if ping.type=='loss'])
	errors = len([ping for ping in window if ping.type=='error'])
	slow_ping = datetime.timedelta(milliseconds=50)
	slow = len([ping for ping in window if ping and ping.latency > slow_ping])
	quality = (total-loss)/total
	return dict(time=window[-1].time, quality=quality, errors=errors,
		loss=loss, slow=slow)

def get_windows(stats):
	"Construct rolling windows"
	windows_ = itertools.islice(windows(stats, n=20), None, None, 10)
	return six.moves.map(get_loss_stats, windows_)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('filename')
	args = parser.parse_args()
	reader = Reader(args.filename)
	stats = reader.get_stats()
	for window in get_windows(stats):
		print(window['time'], window['quality'])

cherrypy = None

class Server(object):
	@classmethod
	def handle_command_line(cls):
		globals().update(cherrypy=importlib.import_module('cherrypy'))
		config = {
			'global': {
				'server.socket_host': '::0',
			}
		}
		cherrypy.quickstart(cls(), config=config)

	def index(self):
		return textwrap.dedent("""
			<!DOCTYPE html>
			<html>
			<body>

			{images}

			</body>
			</html>
			""").format(images='<br/>'.join(self.get_images())).encode('utf-8')
	index.exposed = True

	def get_images(self):
		reader = Reader('ping-results.txt')
		stats = reader.get_stats()
		for day, day_stats in itertools.groupby(stats, lambda res: res.date):
			yield self.make_image(day, day_stats)

	def make_image(self, day, stats):
		# timeseries likes date/value pairs flattened
		data = list(recipes.flatten(
			[str(window['time']), window['quality']]
			for window in get_windows(stats)
		))
		g = time_series.Plot({})
		g.timescale_divisions = '4 hours'
		g.show_x_guidelines=True
		g.x_label_format = '%H:%M'
		g.width=1400
		g.height=800
		g.graph_title=str(day)
		g.show_graph_title=True
		g.add_data(dict(
			data=data,
			title='Network Quality',
		))
		return g.burn().decode('utf-8')

if __name__ == '__main__':
	Server.handle_command_line()
