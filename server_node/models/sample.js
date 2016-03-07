'use strict';

const TYPE2CODE = {
	wind: 1,
	gust: 2,
	direction: 3,
	temperature: 4
};

const TYPE2SCALE = {
	wind: 10,
	gust: 10,
	direction: 1,
	temperature: 10
};

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
			primaryKey: true,
			default: 0
		},
		data: {
			type: DataTypes.INTEGER,
			field: '_data',
			allowNull: false,
			get: function () {
				const type = this.getDataValue('type');
				const data = this.getDataValue('data');
				if (type === TYPE2CODE.wind) {
					return data / TYPE2SCALE.wind;
				} else if (type === TYPE2CODE.gust) {
					return data / TYPE2SCALE.gust;
				} else if (type === TYPE2CODE.direction) {
					return data / TYPE2SCALE.direction;
				} else if (type === TYPE2CODE.temperature) {
					return data / TYPE2SCALE.temperature;
				} else {
					throw new Error(`Unknown sample type: ${type}`);
				}
			},
			set: function (value) {
				const type = this.getDataValue('type');
				if (!type) {
					throw new Error(`Type must be set before data`);
				}
				if (type === TYPE2CODE.wind) {
					this.setDataValue('data', value * TYPE2SCALE.wind);
				} else if (type === TYPE2CODE.gust) {
					this.setDataValue('data', value * TYPE2SCALE.gust)
				} else if (type === TYPE2CODE.direction) {
					this.setDataValue('data', value * TYPE2SCALE.direction)
				} else if (type === TYPE2CODE.temperature) {
					this.setDataValue('data', value * TYPE2SCALE.temperature)
				} else {
					throw new Error(`Unknown sample type: ${type}`);
				}
			}
		}
	}, {
		getterMethods: {
			timestamp: function () {
				return this.dateReported.getTime();
			}
		},
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
	sample.TYPE2CODE = TYPE2CODE;
	sample.TYPE2SCALE = TYPE2SCALE;
	return sample;
};