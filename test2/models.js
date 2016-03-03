'use strict';

const expect = require('chai').expect;

const models = require('./../server2/models');

describe('Models', () => {

	before( () => {
		models.sequelize.sync();
	});

	describe('Sensor', () => {

		beforeEach( () => {
			models.Sensor.destroy({
				force: true,
				truncate: true
			}).then( () => {
				const sensor = models.Sensor.build({
					name: 'Test 1',
					latitude: 1,
					longitude: 2,
					serviceId: 0,
					show: true
				});
				sensor.save().catch( (err) => {
					throw Error('Could not load test data into DB');
				});
			});
		});

		it('Persists new sensor', () => {
			models.Sensor.findAll().then( (sensors) => {
				expect(sensors.length).to.equal(1);
				expect(sensors[0].name).to.equal('Test 1');
			});
		});

	});
});
