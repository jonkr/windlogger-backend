'use strict';

module.exports = function (sequelize, DataTypes) {
	const Sensor = sequelize.define('Sensor', {
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
				Sensor.hasMany(models.Sample)
			}
		},
		timestamps: false,
		underscored: true,
		freezeTableName: true,
		tableName: 'sensors'
	});

	return Sensor;

};