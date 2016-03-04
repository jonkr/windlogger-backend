'use strict';

module.exports = function (sequelize, DataTypes) {
	const sample = sequelize.define('sample', {
		sensorId: {
			type: DataTypes.INTEGER,
			primaryKey: true,
			field: 'sensor_id'
		},
		dateCreated: {
			type: DataTypes.DATE,
			field: 'date_created'
		},
		dateReported: {
			type: DataTypes.DATE,
			primaryKey: true,
			field: 'date_reported'
		},
		type: {
			type: DataTypes.INTEGER,
			primaryKey: true
		},
		data: {
			type: DataTypes.INTEGER,
			field: '_data'
		}
	}, {
		classMethods: {
			associate: function (models) {
				sample.belongsTo(models.sensor, {
					onDelete: "CASCADE",
					foreignKey: {
						allowNull: false
					}
				});
			}
		},
		timestamps: false
	});
	return sample;
};