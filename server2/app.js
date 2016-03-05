const express = require('express');
const routes = require('./routes');
const app = express();

app.use('/', routes);

app.use(function(err, req, res, next) {
	console.log('Detected error:', err);
});

module.exports = app;