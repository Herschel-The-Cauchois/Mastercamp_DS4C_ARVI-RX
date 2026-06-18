const dbConfig = require("../config/db.js")

const Sequelize = require("sequelize")
const sequelize = new Sequelize(dbConfig.DB, dbConfig.USER, dbConfig.PASSWORD, {
    host: dbConfig.HOST,
    dialect: dbConfig.dialect,
    operatorsAliases: false,

    pool: {
        max: dbConfig.pool.max,
        min: dbConfig.pool.min,
        acquire: dbConfig.pool.acquire,
        idle: dbConfig.pool.idle
    }
})

const db = {}

db.Sequelize = Sequelize
db.sequelize = sequelize //Initialization

//All models are based on the given sql schema @ https://github.com/BTajini/assistant-radiologue-virtuel/blob/main/sql/schema.sql
db.case = require("./casesModel.js")(sequelize, Sequelize)
//Note : Sequelize automatically logs creation and update dates in all tables managed by the module. No need to create them manually !

module.exports = db