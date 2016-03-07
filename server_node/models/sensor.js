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
		show: DataTypes.BOOLEAN,
		lastSample: {
			type: DataTypes.STRING,
			field: '_last_samples',
			get: function () {
				return JSON.parse(this.getDataValue('lastSample'));
			},
			set: function(value) {
				this.setDataValue('lastSample', JSON.stringify(value));
			}
		}
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