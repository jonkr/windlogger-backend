#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import logging
import datetime
import requests
import time

import db
from models import Sensor, Sample

log = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)

"""

SMHI API Docs: http://opendata.smhi.se/apidocs/

	API entry-point: http://opendata-download-metobs.smhi.se/api.json

	Byvind: parameter 21
	http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/21.json

	Vindhastighet: parameter 4
	http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/4.json

	Vindriktning: parameter 3
	http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/3.json

"""

BASE_URL = 'http://opendata-download-metobs.smhi.se/api/version/1.0.json'


def get_all_sensors():
    URL = 'http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/4.json'
    resp = requests.get(URL)
    assert resp.status_code == 200, 'Could not fetch station list'
    data = resp.json()
    stations = [
            {
                    'name': s['name'],
                    'id': s['id'],
                    'latitude': s['latitude'],
                    'longitude': s['longitude'],
                    'type': Sensor.TYPE_SMHI
            }
            for s in data['station']
    ]

    for station in stations:
        log.debug('{}: {}, {}'.format(
                station['name'],
                station['latitude'],
                station['longitude']
        ))

    log.info('SMHI: Retrieved SMHI station list: %s', len(stations))
    return stations

def _sensor_transform(sensor):
    """Some SMHI sensors have names ending in '* A', without apparent use to
    to this app. Hence, we'll remove it.
    """
    if sensor.name[-2:] == ' A':
        sensor.name = sensor.name[:-2]
    return sensor


def store_sensors(sensors):
    for sensor_data in sensors:
        sensor = Sensor.query.filter(Sensor.id == sensor_data['id']).scalar()
        if not sensor:
            sensor = Sensor(**sensor_data)
        else:
            log.info('Station %s is already in DB', sensor_data['id'])

        sensor = _sensor_transform(sensor)
        sensor.store()

    log.info('%s SMHI stations in DB',
     Sensor.query.filter(
             Sensor.type == Sensor.TYPES[Sensor.TYPE_SMHI]).count())


def poll_station(sensor):

    SMHI_PARAMS = {
            'wind_speed': 4,
            'wind_gust': 21,
            'wind_direction': 3
    }

    samples = []

    for type_, param in list(SMHI_PARAMS.items()):

        URL = 'http://opendata-download-metobs.smhi.se/api/version/1.0/' \
              'parameter/{param}/station/{station_id}/' \
              'period/latest-day/data.json'.format(
                  param=param, station_id=sensor.id
        )
        resp = requests.get(URL)
        assert resp.status_code in [200, 404], 'Could not poll: {}'.format(URL)

        if resp.status_code == 404:
            log.debug('No %s value for %s (ID=%s) exists', type_, sensor.name,
                      sensor.id)
            continue

        data = resp.json()

        if data['value']:
            samples.append(_create_sample(data, sensor.id, type_))

    return samples


def _create_sample(data, sensor_id, type_):
    last_sample = data['value'][-1]
    timestamp = last_sample['date'] / 1000
    log.debug('Got %s value for %s: %s', type_, sensor_id, last_sample['value'])
    return Sample(
            sensor_id=sensor_id,
            date_reported=datetime.datetime.fromtimestamp(timestamp),
            type=type_,
            data=float(last_sample['value'])
    )


def store_samples(samples):
    updated_sensor_ids = set()
    for sample in samples:
        if Sample.exists(sample.sensor_id, sample.type, sample.date_reported):
            log.info('SMHI: Sample already exists %s', sample)
            continue

        sample.store()
        log.info('SMHI: Stored sample type %s for sensor %s', sample.type,
                                 sample.sensor_id)
        updated_sensor_ids.add(sample.sensor_id)

    return updated_sensor_ids

def poll_all(poll_hidden=False):
    t0 = time.time()
    updated_sensor_ids = set()
    sensors = Sensor.get_all_of_type(Sensor.TYPE_SMHI)
    for sensor in sensors:
        samples = poll_station(sensor)
        updated_sensor_ids.update(store_samples(samples))

    dur = time.time() - t0
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.info('SMHI: Poll completed at %s in %s s.\n'
                     'Polled %s sensors.\n'
                     'Updated %s values.',
                     now, '{:.1f}'.format(dur), len(sensors), len(updated_sensor_ids))
    return updated_sensor_ids


def update_sensor_list():
    stations = get_all_sensors()
    store_sensors(stations)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    db.init()

    parser = argparse.ArgumentParser()
    parser.add_argument(
            'mode',
            help='Operation to run',
            choices=[
                    'get-sensors',
                    'poll-all'
            ])

    args = parser.parse_args()

    if args.mode == 'get-sensors':
        update_sensor_list()

    elif args.mode == 'poll-all':
        poll_all()
