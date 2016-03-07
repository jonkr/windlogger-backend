const express = require('express');
const morgan = require('morgan');
const routes = require('./routes');
const app = express();

app.use('/', routes);

app.use(morgan('combined'));

app.use(function(err, req, res, next) {
	console.log('Detected error:', err);
});

module.exports = app;