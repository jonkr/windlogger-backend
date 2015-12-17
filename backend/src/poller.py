#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import time
import functools
import schedule
import traceback

import db
import utils
from models.wind import Sensor
import poller_viva, poller_weatherlink, poller_smhi

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s %(message)s'
)
logging.getLogger("requests").setLevel(logging.WARNING)
log = logging.getLogger('poller')


notified_errors = set()

def catch_exceptions(job_func):
	@functools.wraps(job_func)
	def wrapper(*args, **kwargs):
		try:
			job_func(*args, **kwargs)
		except Exception as e:
			print(traceback.format_exc())
			log.exception('Error when polling')
			if type(e) not in notified_errors:
				utils.send_email_error_report('Windlogger.se - ERROR', e.message)
				notified_errors.add(type(e))
			else:
				log.debug('Error of type %s already notified.', type(e))
	return wrapper

def update_sample_cache(sensor_ids, update_all=False):
	# Update last sample cache
	t0 = time.time()

	if sensor_ids == set([]) and not update_all:
		log.debug('No updated sensors')
		return
	if sensor_ids:
		sensors = Sensor.query.filter(Sensor.id.in_(sensor_ids)).all()
	elif update_all:
		sensors = Sensor.query.all()

	for sensor in sensors:
		sensor.update_last_sample()

	log.info('Updated last sample caches for {} sensors in '
	         '{:.1f} seconds'.format(len(sensors), time.time() - t0))

@catch_exceptions
def p_weatherlink():
	updated_sensor_ids = poller_weatherlink.poll_all()
	update_sample_cache(updated_sensor_ids)


@catch_exceptions
def p_viva():
	updated_sensor_ids = poller_viva.poll_all()
	update_sample_cache(updated_sensor_ids)

@catch_exceptions
def p_smhi():
	updated_sensor_ids = poller_smhi.poll_all()
	update_sample_cache(updated_sensor_ids)


if __name__ == '__main__':

	db.init()

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'mode',
		help='Operation to run',
		choices=[
			'viva',
			'smhi',
			'weatherlink',
			'update-map-cache'
		])

	args = parser.parse_args()

	if args.mode == 'viva':
		p_viva()
		schedule.every(2).minutes.do(p_viva)

	elif args.mode == 'smhi':
		p_smhi()
		schedule.every(10).minutes.do(p_smhi)

	elif args.mode == 'weatherlink':
		p_weatherlink()
		schedule.every(2).minutes.do(p_weatherlink)

	elif args.mode == 'update-map-cache':
		update_sample_cache([], update_all=True)
		exit(0)

	else:
		raise Exception('Unknown mode: ' + args.mode)

	log.info('Scheduled jobs:')
	for job in schedule.jobs:
		log.info('    ' + str(job))

	while True:
		schedule.run_pending()
		time.sleep(5)



