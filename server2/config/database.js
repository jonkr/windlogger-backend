'use strict';

const CREDS = require('./../../credentials');

const DB_USERNAME = 'windlogger';
const DB_PASSWORD = CREDS.postgresPassword;
const DB_NAME = 'windlogger';

let DB_URI;
if (process.env.WINDLOGGER_ENV === 'dev') {
	DB_URI = `postgres://localhost/${DB_NAME}`;
} else {
	DB_URI = `postgres://${DB_USERNAME}:${DB_PASSWORD}@localhost/${DB_NAME}`;
}

module.exports = {
	DB_URI,
	DB_USERNAME,
	DB_NAME,
	DB_PASSWORD
};
