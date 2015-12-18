#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import locale
import logging
import bs4
import requests
import datetime

from models.wind import Sensor, Sample
import db

KMPH_2_MPS = 0.277778
MPH_2_MPS = 0.44704


log = logging.getLogger(__name__)


WEATHERLINK_BASE_URL = r'http://www.weatherlink.com/user/{user}/index.php?view=summary&headers=2'

SENSORS = [
	dict(
		id=10000,
		name=u'Dalarö Schweizerbadet',
		service_id=u'kitenation',
		type=Sensor.TYPE_WEATHERLINK,
		latitude=59.135164,
		longitude=18.400687,
	),
	dict(
		id=10001,
		name=u'Goekboet',
		service_id=u'gerhen',
		type=Sensor.TYPE_WEATHERLINK,
		latitude=55.486676,
		longitude=14.303449,
	),
	dict(
		id=10002,
		name=u'Lomma Hamn',
		service_id=u'lommahamn',
		type=Sensor.TYPE_WEATHERLINK,
		latitude=55.674827,
		longitude=13.060893,
	),
	dict(
		id=10003,
		name=u'Barsebäck Hamn',
		service_id=u'barsebackshamn',
		type=Sensor.TYPE_WEATHERLINK,
		latitude=55.756530,
		longitude=12.903417,
	),
	dict(
		id=10004,
		name=u'Nidingen',
		service_id=u'nidingen',
		type=Sensor.TYPE_WEATHERLINK,
		latitude=57.303146,
		longitude=11.901856,
	)
]

def create_sensors():
	for sensor in SENSORS:
		if not Sensor.get_by_id(sensor['id']):
			s = Sensor(**sensor)
			s.store()


def get_html(url):
	resp = requests.get(url)
	assert resp.status_code == 200, 'Could not get HTML data'
	return resp.text


def get_body(html_data):
	root = bs4.BeautifulSoup(html_data, 'html.parser')
	body = root.find('body')
	assert body, 'No body!'
	return body


def parse_timestamp(body):
	# Set locale to EN in order to parse timestamp strings correctly
	tds = body.find_all('td', class_=u'summary_timestamp')
	assert len(tds) == 1, 'Ambiguous timestamp'
	stamp = tds[0].text
	preamble = 'Current Conditions as of '
	assert stamp.startswith(preamble), 'Unknown timestamp preamble'
	stamp = stamp[len(preamble):]
	return datetime.datetime.strptime(stamp, '%H:%M %A, %B %d, %Y')


def _parse_speed_value(raw):
	if raw.endswith(' km/h'):
		raw = raw[0:-len(' km/h')]
		return KMPH_2_MPS * float(raw)
	elif raw.endswith(' m/s'):
		raw = raw[0:-len(' m/s')]
		return float(raw)
	elif raw.endswith(' Mph'):
		raw = raw[0:-len(' Mph')]
		return MPH_2_MPS * float(raw)
	elif raw=='Calm':
		return 0
	elif raw == 'n/a':
		return None
	else:
		raise AssertionError('Unknown speed unit for: %s', raw)


def parse_wind_current(body):
	el = body.find('td', class_='summary_data', text='Wind Speed')
	assert el is not None
	siblings = el.parent.findChildren()
	assert len(siblings) > 1
	speed_raw = siblings[1].text
	return _parse_speed_value(speed_raw)

def parse_wind_gust(body):
	el = body.find('td', class_='summary_data', text='Wind Gust Speed')
	assert el is not None
	siblings = el.parent.findChildren()
	assert len(siblings) > 2
	g_speed_raw = siblings[2].text
	return _parse_speed_value(g_speed_raw)

def parse_temperature(body):
	el = body.find('td', class_='summary_data', text='Outside Temp')
	assert el is not None
	siblings = el.parent.findChildren()
	assert len(siblings) > 1
	temp_raw = siblings[1].text
	if temp_raw.endswith(' C'):
		convert = False
	elif temp_raw.endswith(' F'):
		convert = True
	else:
		raise AssertionError('Unknown temperature unit')
	temp_raw = temp_raw[0:-2]
	temp = float(temp_raw)
	if convert:
		temp = (temp - 32) * 5.0/9
	return temp

def parse_wind_dir(body):
	el = body.find('td', class_='summary_data', text='Wind Direction')
	assert el is not None
	siblings = el.parent.findChildren()
	assert len(siblings) > 1
	dir_raw = siblings[1].text
	assert dir_raw.endswith(u'\xb0'), 'No degree symbol where expected'
	dir_raw = dir_raw[0:-1]
	assert u'\xa0' in dir_raw, 'No separation symbol where expected'
	dir_raw = dir_raw.split(u'\xa0')[1]
	return int(dir_raw)


def store(sensor, time_stamp, temperature, wind_current, wind_gust, wind_dir):

	# NOTE: Because Weatherlink values all have the same timestamp, we only wrap
	# the first *.store() in order to detect collision.
	if Sample.query.\
			filter(Sample.sensor_id==sensor.id).\
			filter(Sample.date_reported==time_stamp).all():
		log.info('Sensor %s: Sample @%s already in DB.', sensor.name, time_stamp)
		return None

	if _is_number(wind_current):
		s = Sample(
			sensor_id=sensor.id,
			date_reported=time_stamp,
			type=Sample.TYPE_WIND_SPEED,
			data=wind_current,
		)
		s.store()

	if _is_number(wind_gust):
		s = Sample(
			sensor_id=sensor.id,
			date_reported=time_stamp,
			type=Sample.TYPE_WIND_GUST,
			data=wind_gust
		)
		s.store()

	if _is_number(wind_dir):
		s = Sample(
			sensor_id=sensor.id,
			date_reported=time_stamp,
			type=Sample.TYPE_WIND_DIR,
			data=wind_dir
		)
		s.store()

	if _is_number(temperature):
		s = Sample(
			sensor_id=sensor.id,
			date_reported=time_stamp,
			type=Sample.TYPE_TEMPERATURE,
			data=temperature
		)
		s.store()

	log.info('Sensor %s: Sample @ %s stored in DB', sensor.name, time_stamp)

	return sensor.id

def _is_number(value):
	return type(value) == float or type(value) == int


def poll_sensor(sensor):

	try:

		url = WEATHERLINK_BASE_URL.format(user=sensor.service_id)

		html = get_html(url)
		body = get_body(html)

		time_stamp = parse_timestamp(body)
		temperature = parse_temperature(body)
		wind_current = parse_wind_current(body)
		wind_gust = parse_wind_gust(body)
		wind_dir = parse_wind_dir(body)

		sensor_id = store(sensor, time_stamp, temperature, wind_current, wind_gust,
					 wind_dir)

	except Exception:
		log.exception('Could not poll/parse sensor: %s', sensor.id)
		sensor_id = None

	return sensor_id

def set_locale():
	try:
		locale.setlocale(locale.LC_ALL, 'en_US.utf8')
	except:
		locale.setlocale(locale.LC_ALL, 'en_US')


def poll_all():

	create_sensors()
	set_locale()
	updated_sensor_ids = set()

	for s in SENSORS:
		sensor = Sensor.get_by_id(s['id'])
		updated = poll_sensor(sensor)
		if updated:
			updated_sensor_ids.add(s['id'])

	return updated_sensor_ids


if __name__ == '__main__':

	logging.basicConfig(level=logging.INFO)
	db.init()

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'mode',
		help='Operation to run',
		choices=['get-sensors', 'poll-all'])

	args = parser.parse_args()

	if args.mode == 'get-sensors':
		create_sensors()

	elif args.mode == 'poll-all':
		poll_all()
