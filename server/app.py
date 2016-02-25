import logging
from collections import namedtuple

from flask import Flask, request, jsonify, send_from_directory, render_template
from models import Sample, Sensor
import config
import db
import errors

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

db.init()

CoordScope = namedtuple('CoordScope', ['lat_min', 'lat_max', 'lng_min', 'lng_max'])

@app.route('/api/sensors')
def api_sensors():
	"""List all sensors"""
	show_hidden = request.args.get('hidden', False)
	coord_scope = get_coord_scope(request.args)
	query = Sensor.query
	if not show_hidden:
		query = query.filter(Sensor.show == True)
	if coord_scope:
		query = filter_sensor_coords(query, coord_scope)
	query = query.order_by(Sensor.id)
	sensors = query.all()
	data = [s.format() for s in sensors]
	return jsonify(data=data)


@app.route('/api/sensors/<int:id>')
def api_sensor(id):
	"""List specific sensor"""
	sensor = Sensor.get_by_id(id)
	return jsonify(sensor.format())


@app.route('/api/sensors/<int:id>/data')
def api_sensor_data(id):
	span = parse_int(request.args.get('span', 2))
	span = min(span, config.MAX_HISTORY)

	Sensor.get_by_id_or_404(id)

	samples = {
		sample_type: Sample.get_last(id, type=sample_type, hours=span)
		for sample_type in [
			Sample.TYPE_WIND_SPEED,
			Sample.TYPE_WIND_GUST,
			Sample.TYPE_WIND_DIR
		]
	}

	data = [
		{
			'data': [
				[s.timestamp, s.data]
				for s in samples[Sample.TYPE_WIND_SPEED]
			],
			'name': 'wind'
		},
		{
			'data': [
				[s.timestamp, s.data]
				for s in samples[Sample.TYPE_WIND_GUST]
			],
			'name': 'gust'
		},
		{
			'data': [
				[s.timestamp, s.data]
				for s in samples[Sample.TYPE_WIND_DIR]
			],
			'name': 'direction'
		},
	]

	return jsonify(data=data)


@app.errorhandler(Exception)
def global_error_handler(error):
	if isinstance(error, errors.AppSpecificError):
		return jsonify(error.format()), error.status_code
	else:
		log.error(error.message)
		return jsonify(message='Internal server error', code=500), 500


@app.after_request
def custom_response_headers(response):
	response.headers['X-Api-Version'] = config.API_VERSION
	return response


def parse_int(str, default=2):
	try:
		return int(str)
	except (ValueError, TypeError):
		log.error('Could not parse integer')
		return default


def get_coord_scope(args):
	if request.args.get('latMin'):
		return CoordScope(
			lat_min=request.args.get('latMin'),
			lat_max=request.args.get('latMax'),
			lng_min=request.args.get('lngMin'),
			lng_max=request.args.get('lngMax')
		)
	else:
		return None

def filter_sensor_coords(query, coord_scope):
	return query\
		.filter(Sensor.latitude <= coord_scope.lat_max)\
		.filter(Sensor.latitude >= coord_scope.lat_min)\
		.filter(Sensor.longitude <= coord_scope.lng_max)\
		.filter(Sensor.longitude >= coord_scope.lng_min)


if __name__ == '__main__':

	app.run(port=5000, debug=config.DEBUG, host='0.0.0.0')
	
