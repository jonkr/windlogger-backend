'use strict';

module.exports = function (sequelize, DataTypes) {
	const Sample = sequelize.define('Sample', {
		id: {
			type: DataTypes.INTEGER,
			primaryKey: true
		},
		dateCreated: DataTypes.DATE,
		dateReported: {
			type: DataTypes.DATE,
			primaryKey: true
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
				Sample.belongsTo(models.Sensor, {
					onDelete: "CASCADE",
					foreignKey: {
						allowNull: false
					}
				});
			}
		},
		timestamps: false,
		underscored: true,
		freezeTableName: true,
		tableName: 'samples'
	});

	return Sample;
};