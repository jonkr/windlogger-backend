#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse, time

import json
import logging
import datetime

import requests
from suds.client import Client

import db
from models.wind import Sensor, Sample

log = logging.getLogger(__name__)

STATION_LIST_URL = r'https://services.viva.sjofartsverket.se:8080/' \
                   r'output/vivaoutputservice.svc/vivastation/'
STATION_DATA_URL = STATION_LIST_URL + r'{station_id}'

def get_all_sensors(session):

	viva_id_blacklist = [
		81,   # Icebreaker: Atle (variable coordinates)
		82,   # Icebreaker: Frej (variable coordinates)
		83,   # Icebreaker: Oden (variable coordinates)
		96,   # Icebreaker: Ymer (variable coordinates)
		114,  # Icebreaker: Ale (variable coordinates)
	]

	resp = session.get(STATION_LIST_URL)
	assert resp.status_code == 200
	data = resp.json()
	assert 'GetStationsResult' in data
	assert 'Stations' in data['GetStationsResult']

	sensors = {}
	for sensor in data['GetStationsResult']['Stations']:
		if sensor['ID'] in viva_id_blacklist:
			log.info('Skipping blacklisted sensor %s', sensor['Name'])
			continue
		data = {
			'name': sensor['Name'],
			'id': sensor['ID'],
			'longitude': sensor['Lon'],
			'latitude': sensor['Lat'],
			'type': Sensor.TYPE_VIVA
		}
		log.info(json.dumps(data, sort_keys=True))
		sensors.update({data['id']: data})
	return sensors

def store_sensors(session, sensors, clear_stale_sensors=True):

	if clear_stale_sensors:
		viva_sensors = Sensor.query.filter(
			Sensor.type == Sensor.TYPES['viva']).all()
		for vs in viva_sensors:
			last_24h = Sample.get_last(vs.id, Sample.TYPE_WIND_SPEED, hours=24)
			if not last_24h:
				log.info('No samples for %s during the last 24 h. '
				         'Deleting.', vs.id)
				vs.delete()


	for id, sensor in sensors.items():
		if poll_sensor(session, id):
			viva_sensor = Sensor.query.filter(Sensor.id == id).scalar()
			if not viva_sensor:
				viva_sensor = Sensor(**sensor)
				viva_sensor.store()

	log.info('%s sensors in DB.', Sensor.query.filter(
		Sensor.type == Sensor.TYPES[Sensor.TYPE_VIVA]).count())

def _parse_update_time(time_string):
		return datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")

def _type_of_interest(data_type):
	return data_type in ['Medelvind', 'Byvind', 'Riktning']

def _parse_wind_speed(raw_value_string):
	value = raw_value_string[2:]
	return float(value)

def _too_old(sensor_id, raw_sample):
	AGE_LIMIT_IN_DAYS = 7
	updated = _parse_update_time(raw_sample['Updated'])
	dT = datetime.datetime.utcnow() - updated
	is_too_old = dT > datetime.timedelta(days=AGE_LIMIT_IN_DAYS)
	if is_too_old:
		log.warning(u'Sample {type} for sensor {sid} is older'
		            u' than {limit} days, skipping'.format(
						type=raw_sample['Name'],
                        limit=AGE_LIMIT_IN_DAYS,
						sid=sensor_id))
	return is_too_old

def _parse_viva_sensor_data(sensor_id, raw_samples):

	samples = []

	for raw_sample in raw_samples:

		if not _type_of_interest(raw_sample['Name']):
			continue

		if _too_old(sensor_id, raw_sample):
			continue

		if raw_sample['Name'] == 'Medelvind':

			assert raw_sample['Unit'] == 'm/s', 'Unknown unit: {}'.format(
				raw_sample['Unit'])
			assert raw_sample['Updated'] is not None
			updated = _parse_update_time(raw_sample['Updated'])
			try:
				speed_value = _parse_wind_speed(raw_sample['Value'])
			except ValueError as e:
				log.warning('Sensor: %s, Could not parse wind speed from: %s',
				            sensor_id, raw_sample['Value'])
				continue

			samples.append(Sample(
				sensor_id=sensor_id,
				date_reported=updated,
				type='wind_speed',
				data=speed_value,
			))

			# Get heading from Medelvind!
			heading_value = raw_sample['Heading']
			samples.append(Sample(
				sensor_id=sensor_id,
				date_reported=updated,
				type='wind_direction',
				data=heading_value
			))

		if raw_sample['Name'] == 'Byvind':
			assert raw_sample['Unit'] == 'm/s', 'Unknown unit: {}'.format(
				raw_sample['Unit'])
			assert raw_sample['Updated'] is not None
			updated = _parse_update_time(raw_sample['Updated'])
			try:
				gust_speed_value = _parse_wind_speed(raw_sample['Value'])
			except ValueError as e:
				log.warning('Sensor: %s, Could not parse wind speed from: %s',
				            sensor_id, raw_sample['Value'])
				continue

			samples.append(Sample(
				sensor_id=sensor_id,
				date_reported=updated,
				type='wind_gust',
				data=gust_speed_value
			))

	return samples

def poll_sensor(session, sensor_id):
	resp = session.get(STATION_DATA_URL.format(station_id=sensor_id))
	assert resp.status_code == 200
	data = resp.json()
	assert 'GetSingleStationResult' in data
	assert 'Samples' in data['GetSingleStationResult']
	raw_samples = data['GetSingleStationResult']['Samples']
	if raw_samples is None:
		log.warning('No data for sensor %s', sensor_id)
		return []
	samples = _parse_viva_sensor_data(sensor_id, raw_samples)
	return samples

def store_samples(samples):
	updated_sensor_ids = set()
	for sample in samples:
		if Sample.exists(sample.sensor_id,
						 sample.type, sample.date_reported):
			continue
		sample.store()
		updated_sensor_ids.add(sample.sensor_id)
	return updated_sensor_ids

def poll_all():
	log.info('VIVA: Polling all sensors')

	session = requests.Session()

	t0 = time.time()
	sensors = Sensor.get_all_of_type(Sensor.TYPE_VIVA)
	updated_sensor_ids = set()
	for s in sensors:
		samples = poll_sensor(session, s.id)
		updated_sensor_ids.update(store_samples(samples))

	dur = time.time() - t0
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	log.info('VIVA: Poll completed at %s in %s s.', now, '{:.1f}'.format(dur))
	log.info('VIVA: %s sensors were updated', len(updated_sensor_ids))
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
		session = requests.Session()
		sensors = get_all_sensors(session)
		log.info('Fetched %s ViVa locations', len(sensors))
		store_sensors(session, sensors)

	elif args.mode == 'poll-all':
		poll_all()
