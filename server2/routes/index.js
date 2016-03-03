'use strict';

const models = require('../models');
const express = require('express');
const router = express.Router();

router.get('/api/sensors', function (req, res) {
	models.Sensor.findAll().then( sensors => {
		res.send(sensors);
	})
});

module.exports = router;