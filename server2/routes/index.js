'use strict';

const models = require('../models');
const express = require('express');
const router = express.Router();

router.get('/api/sensors', (req, res) => {
	models.Sensor.findAll().then( sensors => {
		res.send(sensors);
	})
});

router.get('/api/sensors/:id', (req, res) => {
	models.Sensor.findOne({
		where: {
			id: req.params.id
		}
	}).then( sensor => {
		res.send(sensor);
	})
});

router.get('/api/sensors/:id/data', (req, res) => {
	models.Sensor.findOne({
		where: {
			id: req.params.id
		}
	}).then( sensor => {
		models.Sample.findAll({
			where: {
				dateReported: {
					sensorId: req.params.id,
					$gte: moment().subtract(24, 'hours')
				}
			}
		})
	})
});

module.exports = router;