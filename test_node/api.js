'use strict';

const app = require('../server_node/app');
const request = require('supertest');
const models = require('../server_node/models');
const expect = require('chai').expect;

describe('GET /api/sensors', () => {

	before( done => {
		models.sequelize.sync().then( () => {
			done();
		});
	});

	it('responds with json', done => {
		request(app)
			.get('/api/sensors')
			.expect('Content-Type', /json/)
			.expect(200, done);
	});

	describe('GET /api/sensors/:id', () => {

		it('correctly handles missing sensor', done => {
			request(app)
				.get('/api/sensors/999999')
				.expect('Content-Type', /json/)
				.expect(404, done)
		});

	});

});
