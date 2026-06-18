module.exports = (sequelize, Sequelize) => {
    const Case = sequelize.define("case", {
        id: {
            type: Sequelize.INTEGER,
            primaryKey: true,
            autoIncrement: true,
            allowNull: false
        },
        imgPath: {
            type: Sequelize.TEXT,
            allowNull: false
        },
        source: {
            type: Sequelize.TEXT
        },
        ground_truth_label: {
            type: Sequelize.STRING(50) //No need for unlimited text size here, strict necessary
        },
        split: {
            type: Sequelize.STRING(50),
            allowNull: false
        },
        notes: {
            type: Sequelize.TEXT
        }
    })
}