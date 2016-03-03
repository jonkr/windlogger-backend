const pg = require('pg');

const DB_CONF = require('./config/database');

const client = new pg.Client(DB_CONF.DB_URI);

client.connect(function (err) {
	if (err) {
		return console.error('Could not connect to postgres', err);
	}
	client.query('SELECT COUNT(*) FROM sensors', function (err, result) {
		if (err) {
			return console.error('Error running query', err);
		}
		console.log(result.rows);
		client.end();
	})
});
