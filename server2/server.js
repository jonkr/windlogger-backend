'use strict';

const Sequelize = require('sequelize');
const DB = require('./config/database');
const express = require('express');
const PORT = 3000;

const sequelize = new Sequelize(DB.DB_URI, {
	host: 'localhost',
	dialect: 'postgres',

	pool: {
		max: 5,
		min: 0,
		idle: 5000
	},

	define: {
		timestamps: false
	}

});

const Sensor = sequelize.define('sensor', {
	name: {
		type: Sequelize.STRING
	},
	type: {
		type: Sequelize.INTEGER
	},
	latitude: {
		type: Sequelize.FLOAT
	},
	longitude: {
		type: Sequelize.FLOAT
	},
	serviceId: {
		type: Sequelize.STRING,
		field: 'service_id'
	},
	show: {
		type: Sequelize.BOOLEAN
	}
});

sequelize.sync(); // Create any missing tables

Sensor.all().then(function (sensors) {
	console.log(`Found ${sensors.length} sensors`);
});

const app = express();

app.get('/api/sensors', function (req, res) {
	Sensor.all().then(function (sensors) {
		res.send(sensors);
	})
});

app.listen(PORT, function () {
	console.log(`Windlogger backend listening on ${PORT}`);
});

