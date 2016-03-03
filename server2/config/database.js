const CREDS = require('./../../credentials');

const DB_USERNAME = 'windlogger';
const DB_PASSWORD = CREDS.postgresPassword;
const DB_NAME = 'windlogger';
//const DB_URI = `postgres://${DB_USERNAME}:${DB_PASSWORD}@localhost/${DB_NAME}`;
const DB_URI = `postgres://localhost/${DB_NAME}`;


module.exports = {
	DB_URI
};
