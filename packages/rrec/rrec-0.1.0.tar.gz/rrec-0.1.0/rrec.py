#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rrec - automatically record your favourite program from WDR radio

This script will download and parse the program listings of different WDR radio
stations, grep them for preconfigured words and writes streamripper cronjobs to
record them.

see ``rrec -h`` for usage help

As this script only creates cronjobs, ``cron`` and ``streamripper`` are
required to actually record the programs.

copyright (c) 2013 Tobias Bengfort <tobias.bengfort@gmx.net>
license: GPL-3+
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from datetime import datetime, timedelta
import os
import sqlite3

try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen

from crontab import CronTab


# config
WORKING_DIR = os.path.expanduser('~/.rrec/')
DATABASE = WORKING_DIR + 'db.sqlite'
TARGET_DIR = '~/.rrec/rec/'
WORDS = [
	'SpielArt',
	'Roger',
	'Hörspiel',
	'Krimi',
	'Kabarett',
	'Unterhaltung',
	'Ohrclip',
]
ACTIVE_CHANNELS = ['radio5']

AVAILABLE_CHANNELS = {
	'1live': 'http://www.wdr.de/wdrlive/media/einslive.m3u',
	'wdr2': 'http://www.wdr.de/wdrlive/media/wdr2.m3u',
	'wdr3': 'wdr3 http://www.wdr.de/wdrlive/media/wdr3.m3u',
	'wdr4': 'http://www.wdr.de/wdrlive/media/wdr4.m3u',
	'radio5': 'http://www.wdr.de/wdrlive/media/wdr5.m3u',
	'europa': 'http://www.wdr.de/wdrlive/media/fhe.m3u',
	'kiraka': 'http://www.wdr.de/wdrlive/media/kiraka.m3u',
}


if not os.path.exists(WORKING_DIR):
	os.makedirs(WORKING_DIR)


def get_db():
	detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
	return sqlite3.connect(DATABASE, detect_types=detect_types)


def _get(week, channel):
	week = ('0' + str(week))[-2:]
	url = "http://www.wdr.de/epg/download/dl/{}{}.txt".format(week, channel)
	return urlopen(url).read().decode('ISO-8859-1')


def _parse(s, channel):
	lines = s.split('\r\n\r\n')
	items = []

	for line in lines[1:-1]:
		line = line.strip()
		if not line[0].isdigit():  # line is date
			# e.g. Samstag, den 16.02.2013
			date = line[-10:]
		else:  # line is item
			line = line.split('\t', 2)
			line = (line + ['', ''])[:3]
			t, title, comment = line
			# if date is not defined, raise an error
			dt = datetime.strptime(date + t, '%d.%m.%Y%H:%M')

			# set duration of prior item
			if len(items) >= 1:
				delta = dt - items[-1]['dt']
				items[-1]['minutes'] = int(delta.total_seconds() / 60)

			items.append({
				'dt': dt,
				'title': title.strip(),
				'comment': comment,
				'channel': channel,
			})

	# set duration for final item
	if len(items) >= 1:
		delta = items[-1]['dt'] - datetime.strptime(date, '%d.%m.%Y')
		items[-1]['minutes'] = int(24 * 60 - delta.total_seconds() / 60)

	return items


def _write_db(items):
	db = get_db()
	db.execute("""CREATE TABLE IF NOT EXISTS items (
		channel TEXT,
		dt TIMESTAMP,
		minutes INTEGER,
		title TEXT,
		comment TEXT,
		UNIQUE (channel, dt)
		ON CONFLICT REPLACE);""")
	db.executemany("""INSERT INTO items (channel, dt, minutes, title, comment)
		VALUES (:channel, :dt, :minutes, :title, :comment)""", items)
	db.commit()


def update(n=4):
	current_week = int(datetime.now().strftime('%U'))
	for channel in ACTIVE_CHANNELS:
		for week in range(current_week, current_week + n):
			s = _get(week, channel)
			items = _parse(s, channel)
			_write_db(items)


def clean_db():
	"""Delete past items from database."""
	db = get_db()
	db.execute('DELETE FROM items WHERE dt < datetime("now")')
	db.commit()


def crontab(items, show_only=False, padding=60):
	cmd = 'streamripper {} -d {} -A -a "{}_{}" -l {} > /dev/null 2>&1 # rrec'
	tab = CronTab(tab='# rrec result') if show_only else CronTab()

	# clear old
	tab.remove_all('rrec')

	for item in items:
		job = tab.new(command=cmd.format(
			AVAILABLE_CHANNELS[item['channel']],
			TARGET_DIR,
			item['dt'].strftime('%Y%m%d'),
			item['title'],
			item['minutes'] * 60 + 2 * padding))
		start = item['dt'] - timedelta(seconds=padding)
		job.minute.on(start.minute)
		job.hour.on(start.hour)
		job.dom.on(start.day)
		job.month.on(start.month)
	if show_only:
		print(tab.render())
	else:
		tab.write()


def selection():
	db = get_db()
	template = 'title LIKE :{} OR comment LIKE :{}'
	sql = [template.format(k, k) for k, word in enumerate(WORDS)]
	sql = 'SELECT * FROM items WHERE ' + ' OR '.join(sql)
	cursor = db.execute(sql, ['%{}%'.format(word) for word in WORDS])

	items = list()
	for row in cursor.fetchall():
		item = dict()
		for i, value in enumerate(row):
			field_name = cursor.description[i][0]
			item[field_name] = value
		items.append(item)

	return items


def parse_args():
	import argparse
	from gettext import gettext as _

	parser = argparse.ArgumentParser(
		description=_('automatically record programs from WDR'))
	subparsers = parser.add_subparsers(title=_('actions'))

	parser_update = subparsers.add_parser(
		'update', help=_('update local database'))
	parser_update.set_defaults(action='update')
	parser_update.add_argument(
		'-n', type=int, default=4, help=_('number of weeks to get'))

	parser_clean = subparsers.add_parser(
		'clean', help=_('delete all items from db which are already over'))
	parser_clean.set_defaults(action='clean')

	parser_crontab = subparsers.add_parser(
		'crontab', help=_('generate a crontab'))
	parser_crontab.set_defaults(action='crontab')
	parser_crontab.add_argument('-o', '--show-only', action='store_true',
		help=_('display resulting crontab instead of writing it directly'))
	parser_crontab.add_argument('-p', '--padding', type=int, default=120,
		help=_('additional seconds before and after official start and end times'))

	parser_clean = subparsers.add_parser(
		'all', help=_('update, clean and crontab'))
	parser_clean.set_defaults(action='all')

	return parser.parse_args()


def main():
	args = parse_args()

	if args.action == 'update':
		update(n=args.n)
	elif args.action == 'crontab':
		items = selection()
		crontab(items, show_only=args.show_only, padding=args.padding)
	elif args.action == 'clean':
		clean_db()
	elif args.action == 'all':
		update()
		clean_db()
		l = selection()
		crontab(l)


if __name__ == '__main__':
	main()
