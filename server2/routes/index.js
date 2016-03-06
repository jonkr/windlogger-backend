'use strict';

const express = require('express');
const moment = require('moment');
const _ = require('lodash');

const models = require('../models');
const router = express.Router();


function buildChartData(samples) {
	const speed = _.filter(samples, sample => {
		return models.sample.TYPE2CODE.wind === sample.type;
	});
	const direction = _.filter(samples, sample => {
		return models.sample.TYPE2CODE.direction === sample.type;
	});
	const gust = _.filter(samples, sample => {
		return models.sample.TYPE2CODE.gust === sample.type;
	});
	return [
		{
			data: _.map(speed, s => {return [s.timestamp, s.get('data')]}),
			name: 'wind'
		},
		{
			data: _.map(gust, s => {return [s.timestamp, s.get('data')]}),
			name: 'gust'
		},
		{
			data: _.map(direction, s => {return [s.timestamp, s.get('data')]}),
			name: 'direction'
		}
	];
}

router.get('/api/sensors', (req, res) => {
	models.sensor.findAll().then(sensors => {
		res.send({data: sensors});
	})
});

router.get('/api/sensors/:id', (req, res) => {
	models.sensor.findOne({
		where: {
			id: Number(req.params.id)
		}
	}).then(sensor => {
		if (!sensor) {
			res.status(404).send({
				message: `Sensor ${req.params.id} does not exist`
			})
		} else {
			res.send(sensor);
		}
	})
});

router.get('/api/sensors/:id/data', (req, res, next) => {
	models.sensor.findOne({
		where: {
			id: Number(req.params.id)
		}
	}).then(sensor => {
		if (!sensor) {
			res.status(404).send({
				message: `Sensor ${req.params.id} does not exist`
			});
		} else {
			const hours = Number(req.query.span) || 2;
			return models.sample.findAll({
				where: {
					sensorId: req.params.id,
					dateReported: {
						$gte: moment().subtract(hours, 'hours').format()
					}
				},
				order: [
					['dateReported', 'ASC']
				]
			})
		}
	}).then(samples => {
		res.send({data: buildChartData(samples)});
	}).catch(next);
});

module.exports = router;