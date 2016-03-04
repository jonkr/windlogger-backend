'use strict';

const moment = require('moment');


const expect = require('chai').expect;

const models = require('./../server2/models');

describe('Models', () => {

	before(() => {
		models.sequelize.sync();
	});

	describe('Sensor', () => {

		beforeEach(() => {
			models.sensor.destroy({
				force: true,
				truncate: true
			}).then(() => {
				const sensor = models.sensor.build({
					name: 'Test 1',
					latitude: 1,
					longitude: 2,
					serviceId: 0,
					show: true
				});
				sensor.save().catch((err) => {
					throw Error(err);
				});
			});
		});

		it('Persists new sensor', (done) => {
			models.sensor.findAll().then((sensors) => {
				expect(sensors.length).to.equal(1);
				expect(sensors[0].name).to.equal('Test 1');
				done();
			});
		});

	});

	describe('Sample', () => {

		beforeEach(() => {
			models.sample.destroy({
				force: true,
				truncate: true
			}).then(() => {
				const sample = models.sample.build({
					sensorId: 1,
					dateReported: moment().subtract(1, 'hour').toDate(),
					dateCreated: moment().subtract(1, 'hour').toDate(),
					data: 20,
					type: 0
				});
				sample.save().catch((err) => {
					throw Error(err);
				})
			}).then(() => {
				const sample = models.sample.build({
					sensorId: 1,
					dateReported: moment().subtract(2, 'hour').toDate(),
					dateCreated: moment().subtract(2, 'hour').toDate(),
					data: 10,
					type: 0
				});
				sample.save().catch((err) => {
					throw Error(err);
				})
			})
		});

		it('Persists new sample', (done) => {
			models.sample.findAll({
					where: {
						sensorId: 1
					},
					order: [
						['dateReported', 'ASC']
					]
				})
				.then((samples) => {
					expect(samples.length).to.equal(2);
					expect(samples[0].data).to.equal(10);
					expect(samples[1].data).to.equal(20);
					done();
				});
		});

		it('Correctly filters out old samples', (done) => {
			models.sample.findAll({
					where: {
						sensorId: 1,
						dateReported: {
							$gte: moment().subtract(90, 'minutes').toDate()
						}
					},
					order: [
						['dateReported', 'ASC']
					]
				})
				.then((samples) => {
					expect(samples.length).to.equal(1);
					expect(samples[0].data).to.equal(20);
					done();
				});
		});

	})

});
