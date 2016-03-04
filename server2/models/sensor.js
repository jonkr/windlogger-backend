'use strict';

module.exports = function (sequelize, DataTypes) {
	const sensor = sequelize.define('sensor', {
		id: {
			type: DataTypes.INTEGER,
			primaryKey: true
		},
		name: DataTypes.STRING,
		latitude: DataTypes.FLOAT,
		longitude: DataTypes.FLOAT,
		serviceId: {
			type: DataTypes.INTEGER,
			field: 'service_id'
		},
		show: DataTypes.BOOLEAN
	}, {
		classMethods: {
			associate: function (models) {
				sensor.hasMany(models.sample)
			}
		},
		timestamps: false
	});
	return sensor;
};