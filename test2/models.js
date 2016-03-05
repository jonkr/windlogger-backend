'use strict';

const moment = require('moment');
const expect = require('chai').expect;
const models = require('./../server2/models');

describe('Models', () => {

	beforeEach(done => {
		models.sequelize.sync({force: true})
			.then(() => {
				done();
			});
	});

	describe('Sensor', () => {

		beforeEach(done => {
			const sensor = models.sensor.build({
				id: 1,
				name: 'Test 1',
				latitude: 1,
				longitude: 2,
				serviceId: 0,
				show: true
			});
			sensor.save()
				.then(() => {
					done();
				})
				.catch(err => {
					throw new Error(err);
				});
		});

		it('Persists new sensor', done => {
			models.sensor.findAll().then(sensors => {
				expect(sensors.length).to.equal(1);
				expect(sensors[0].name).to.equal('Test 1');
				done();
			});
		});

	});

	describe('Sample', () => {

		beforeEach((done) => {

			models.sequelize.sync({force: true})
				.then(() => {
					const sensor = models.sensor.build({
						id: 1,
						name: 'Test 1',
						latitude: 1,
						longitude: 2,
						serviceId: 0,
						show: true
					});
					return sensor.save();
				})
				.then(() => {
					const sample = models.sample.build({
						sensorId: 1,
						dateReported: moment().subtract(1, 'hour').toDate(),
						dateCreated: moment().subtract(1, 'hour').toDate(),
						data: 20,
						type: 0
					});
					return sample.save();
				})
				.then(() => {
					const sample = models.sample.build({
						sensorId: 1,
						dateReported: moment().subtract(2, 'hour').toDate(),
						dateCreated: moment().subtract(2, 'hour').toDate(),
						data: 10,
						type: 0
					});
					return sample.save();
				})
				.then(() => {
					done();
				})
				.catch(err => {
					throw new Error(err);
				});
		});

		it('Persists new samples', (done) => {
			models.sample.findAll({
					where: {
						sensorId: 1
					},
					order: [
						['dateReported', 'ASC']
					]
				})
				.then(samples => {
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

	});

});
