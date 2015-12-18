#!/usr/bin/env python
# -*- coding: utf-8 -*-
import calendar
from collections import namedtuple
import logging
import datetime

from sqlalchemy import (Column, Integer, DateTime, String, Float, ForeignKey,
						PickleType, Boolean)

from db import Base
from sqlalchemy.orm import relationship
import errors


log = logging.getLogger(__name__)

class Sensor(Base):
	__tablename__ = 'sensors'

	TYPE_VIVA = 'viva'
	TYPE_WEATHERLINK = 'weatherlink'
	TYPE_SMHI = 'smhi'

	TYPES = {
		TYPE_WEATHERLINK: 1,
		TYPE_VIVA: 2,
		TYPE_SMHI: 3
	}

	CODE_2_TYPE = {
		code: type
		for type, code in TYPES.items()
	}

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	type = Column(Integer, nullable=False)
	latitude = Column(Float, nullable=False)
	longitude = Column(Float, nullable=False)
	service_id = Column(String)
	last_samples = Column(PickleType)
	show = Column(Boolean, default=True)

	data = relationship('Sample', backref='sensor', cascade="all, delete-orphan")

	def __init__(self, id, type, name, latitude, longitude, service_id=None):
		assert type in self.TYPES
		self.id = id
		self.type = self.TYPES[type]
		self.name = name
		self.latitude = latitude
		self.longitude = longitude
		self.service_id = service_id

	@classmethod
	def get_all(cls):
		return cls.query.all()

	@classmethod
	def get_by_id_or_404(cls, id_):
		sensor = cls.query.filter(Sensor.id == id_).scalar()
		if sensor is None:
			raise errors.SensorNotFoundError(id_)
		return sensor

	@classmethod
	def get_all_of_type(cls, type, include_hidden=False):
		assert type in cls.TYPES, 'Unkown type: {}'.format(type)
		query = cls.query.filter(cls.type == cls.TYPES[type])
		if not include_hidden:
			query = query.filter(cls.show == True)
		return query.all()

	def format(self):
		return dict(
			id=self.id,
			name=self.name,
			type=self.CODE_2_TYPE[self.type],
			latitude=self.latitude,
			longitude=self.longitude,
			lastSample=self.last_samples,
			show=self.show
		)

	@property
	def has_recent_samples(self):
		return bool(self.get_recent_samples(Sample.TYPE_WIND_SPEED, hours=24))

	def get_recent_samples(self, sample_type=None, hours=2):
		if sample_type is None:
			sample_type = Sample.TYPE_WIND_SPEED
		return Sample.get_last(self.id, sample_type, hours)

	def update_last_sample(self):
		s_speed = Sample.get_latest(self.id, Sample.TYPE_WIND_SPEED)
		s_dir = Sample.get_latest(self.id, Sample.TYPE_WIND_DIR)

		if s_speed:
			now = datetime.datetime.now()
			age = now - s_speed.date_reported
			max_age = datetime.timedelta(hours=6)
			too_old = age > max_age
		else:
			too_old = True
			self.show = False

		if not too_old and s_speed and s_dir:
			self.last_samples =  {
				'speed': {
					'value': s_speed.data,
					'stamp': s_speed.timestamp
				},
				'windDir': {
					'value': s_dir.data,
					'stamp': s_dir.timestamp
				}
			}
			self.show = True
		else:
			self.last_samples = None

		self.store()

	def __repr__(self):
		return u'<Sensor: name={}, id={}, type={} >'.format(self.name, self.id,
			self.CODE_2_TYPE[self.type])


class Sample(Base):

	__tablename__ = 'samples'

	Type = namedtuple('Type', ['code', 'factor', 'unit'])

	TYPE_WIND_SPEED = 'wind_speed'
	TYPE_WIND_GUST = 'wind_gust'
	TYPE_WIND_DIR = 'wind_direction'
	TYPE_TEMPERATURE = 'temperature'

	TYPES = {
		TYPE_WIND_SPEED: Type(1, 10.0, 'm/s'),
		TYPE_WIND_GUST: Type(2, 10.0, 'm/s'),
		TYPE_WIND_DIR: Type(3, 1.0, '°'),
		TYPE_TEMPERATURE: Type(4, 10.0, '°C'),
	}

	TYPE_2_FACTOR = {
		t.code: t.factor
		for _, t in TYPES.items()
	}

	sensor_id = Column(Integer, ForeignKey('sensors.id'), primary_key=True)
	date_created = Column(DateTime,
						  nullable=False,
						  default=datetime.datetime.utcnow	,
						  index=True)
	date_reported = Column(DateTime, primary_key=True)
	type = Column(Integer, primary_key=True)
	_data = Column(Integer)

	def __init__(self, sensor_id, date_reported, type, data):
		assert type in self.TYPES, 'Unknown type: {}'.format(type)
		self.sensor_id = sensor_id
		self.date_reported = date_reported
		self.type = self.TYPES[type].code
		self._data = int(round(self.TYPES[type].factor * data))

	@property
	def data(self):
		return self._data / self.TYPE_2_FACTOR[self.type]

	@classmethod
	def exists(cls, sensor_id, type, date_reported):
		return bool(cls.query. \
					filter(cls.sensor_id == sensor_id). \
					filter(cls.type == type). \
					filter(cls.date_reported == date_reported).count())

	@classmethod
	def get_last(cls, id, type=None, hours=2):
		then = datetime.datetime.now() - datetime.timedelta(hours=hours)
		if type:
			return cls.query.filter(cls.type == cls.TYPES[type].code) \
				.filter(cls.sensor_id == id) \
				.filter(cls.date_reported >= then) \
				.order_by(cls.date_reported).all()
		else:
			return cls.query \
				.filter(cls.sensor_id == id) \
				.filter(cls.date_reported >= then) \
				.order_by(cls.date_reported).all()

	@classmethod
	def get_latest(cls, id, type):
		"""Return the most recent sample"""
		then = datetime.datetime.utcnow() - datetime.timedelta(days=7)
		return cls.query.filter(cls.type == cls.TYPES[type].code) \
			.filter(cls.sensor_id == id) \
			.filter(cls.date_created >= then) \
			.order_by(cls.date_reported.desc()).first()

	@property
	def timestamp(self, millis=True):
		stamp = calendar.timegm(self.date_reported.timetuple())
		if millis:
			return 1000 * stamp
		else:
			return stamp


	def __repr__(self):
		return '<Sensor ID: {}, Type: {}, Value: {}, Reported: {}'.format(
			self.sensor_id, self.type, self.data, self.date_reported
		)
