'use strict';

const moment = require('moment');


const expect = require('chai').expect;

const models = require('./../server2/models');

describe('Models', () => {

	before( () => {
		models.sequelize.sync();
	});

	describe('Sensor', () => {

		beforeEach( () => {
			models.sensor.destroy({
				force: true,
				truncate: true
			}).then( () => {
				const sensor = models.sensor.build({
					name: 'Test 1',
					latitude: 1,
					longitude: 2,
					serviceId: 0,
					show: true
				});
				sensor.save().catch( (err) => {
					throw Error(err);
				});
			});
		});

		it('Persists new sensor', (done) => {
			models.sensor.findAll().then( (sensors) => {
				expect(sensors.length).to.equal(1);
				expect(sensors[0].name).to.equal('Test 1');
				done();
			});
		});

	});

	describe('Sample', () => {

		beforeEach( () => {
			models.sample.destroy({
				force: true,
				truncate: true
			}).then( () => {
				const sample = models.sample.build({
					sensorId: 1,
					dateReported: moment().subtract(1, 'hour'),
					dateCreated: moment().subtract(1, 'hour'),
					data: 10,
					type: 0
				});
				sample.save().catch( (err) => {
					throw Error(err);
				})
			})
		});

		it('Persists new sample', (done) => {
			models.sample.findAll().then( (samples) => {
				expect(samples.length).to.equal(1);
				expect(samples[0].data).to.equal(10);
				done();
			});
		});
	})

});
