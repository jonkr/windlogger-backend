#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
De-duplicate available sensors from different vendors if they are too close
geographically. When two sensors in close proximity are found, hide the lower
ranking one based on the PRIORITY list.
"""
import argparse
import itertools

from geopy.distance import distance

import db
from models import Sensor, Sample

PRIORITY = {
	Sensor.TYPES[Sensor.TYPE_VIVA]: 3,        # the most reliable and frequent
	Sensor.TYPES[Sensor.TYPE_WEATHERLINK]: 2, #
	Sensor.TYPES[Sensor.TYPE_SMHI]: 1         # reliable, but only hourly data
}

def calc_sensor_distance(s1, s2):
	p1 = (s1.longitude, s1.latitude)
	p2 = (s2.longitude, s2.latitude)
	return distance(p1, p2).meters

def pick_sensor_w_fewest_samples(s1, s2):
	if s1.recent_count < s2.recent_count:
		return s1
	elif s2.recent_count < s1.recent_count:
		return s2
	else:
		raise Exception('Sensors have the same number of recent samples')


def pick_sensor_w_lowest_priority(s1, s2):
	p1 = PRIORITY[s1.type]
	p2 = PRIORITY[s2.type]
	if p1 > p2:
		return s2
	elif p1 < p2:
		return s1
	else:
		raise Exception('Sensors have the same priority')

def select_sensor_to_hide(s1, s2):
	if s1.type == s2.type:
		return pick_sensor_w_fewest_samples(s1, s2)
	else:
		return pick_sensor_w_lowest_priority(s1, s2)

def hide_lowest_ranking_dupe(s1, s2):
	sensor_to_hide = select_sensor_to_hide(s1, s2)
	print u'Hiding sensor: {}'.format(sensor_to_hide)
	sensor_to_hide.show = False
	sensor_to_hide.store()

def list_close_by_sensors(args):

	sensors = Sensor.query.filter(
		Sensor.show == True).all()

	print 'Sensor counts:'
	print 'VIVA : {}'.format(
		len([s for s in sensors if s.type == Sensor.TYPES[Sensor.TYPE_VIVA]]))
	print 'SMHI: {}'.format(
		len([s for s in sensors if s.type == Sensor.TYPES[Sensor.TYPE_SMHI]]))
	print 'WEATHERLINK : {}'.format(
		len([s for s in sensors if s.type == Sensor.TYPES[Sensor.TYPE_WEATHERLINK]]))

	sensors_combo = list(itertools.product(sensors, sensors))

	distances = []
	for idx, (s1, s2) in enumerate(sensors_combo):
		if s1.id == s2.id:
			continue
		d = calc_sensor_distance(s1, s2)
		distances.append((s1, s2, d))

	distances = sorted(distances, key=lambda x: x[-1])

	dupes = filter(lambda x: x[-1] < args.limit, distances)
	print 'Found {} sensors too close to each other:'.format(len(dupes))

	print '{name:<20} {id:<8} {recent:<7} -- ' \
	      '{name:<20} {id:<8} {recent:<7}'.format(name='NAME', id='ID',
	                                              recent='RECENT')
	for dupe in dupes:
		s1 = dupe[0]
		s2 = dupe[1]
		d = dupe[2]

		for s in [s1, s2]:
			recent_samples = s.get_recent_samples(hours=24)
			s.recent_count = len(recent_samples)
			s.info = u'{:<20} {:<8} {:<7}'.format(
				s.name, s.id, s.recent_count)


		print u'{} -- {} :: {:>4.0f}'.format(s1.info, s2.info, d)

	return dupes

def hide_close_by_sensors(args, dupes):
	for dupe in dupes:
		s1 = dupe[0]
		s2 = dupe[1]
		d = dupe[2]

		print u'{:>30} ({:>8}) -- {:>30} ({:>8}): {:>10.0f}'.format(
			s1.name, s1.id, s2.name, s2.id, d)

		hide_lowest_ranking_dupe(s1, s2)


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'mode',
		help='Operation to run',
		choices=['list', 'dedup']
	)
	parser.add_argument(
		'--intra-type',
		dest='intra_type_only',
		help='Only do dedup check between sensors of the same type',
		action='store_true'
	)
	parser.add_argument(
		'--limit',
		type=int,
		help='Maximum distance between duplicate sensors',
		default=2000
	)
	return parser.parse_args()


if __name__ == '__main__':

	args = parse_args()

	db.init()

	if args.mode == 'list':
		list_close_by_sensors(args)
	elif args.mode == 'dedup':
		dupes = list_close_by_sensors(args)
		hide_close_by_sensors(args, dupes)

	sensors_shown = Sensor.query.filter(Sensor.show == True).count()
	sensors_hidden = Sensor.query.filter(Sensor.show == False).count()
	print '{} sensors are shown'.format(sensors_shown)
	print '{} sensors are hidden'.format(sensors_hidden)



