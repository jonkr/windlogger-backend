'use strict';

const CODE2TYPE = {
	1: 'weatherlink',
	2: 'viva',
	3: 'smhi'
};

module.exports = function (sequelize, DataTypes) {
	const sensor = sequelize.define('sensor', {
		id: {
			type: DataTypes.INTEGER,
			primaryKey: true
		},
		name: DataTypes.STRING,
		latitude: DataTypes.FLOAT,
		longitude: DataTypes.FLOAT,
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
		},
		type: {
			type: DataTypes.INTEGER,
			field: 'type',
			get: function () {
				const typeCode = this.getDataValue('type');
				if (!CODE2TYPE.hasOwnProperty(typeCode)) {
					throw new Error(`Unknown type code: ${typeCode}`);
				} else {
					return CODE2TYPE[typeCode];
				}
			}
		}
	}, {
		classMethods: {
			associate: function (models) {
				sensor.hasMany(models.sample)
			}
		},
		instanceMethods: {
			format: function () {
				return {
					name: this.name,
					latitude: this.latitude,
					longitude: this.longitude,
					lastSample: this.lastSample,
					type: this.type,
					id: this.id,
					show: this.show
				}
			}
		},
		timestamps: false
	});
	return sensor;
};