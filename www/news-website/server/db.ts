import mysql from "mysql2/promise";

const config = useRuntimeConfig();
const databaseUser = config.databaseUser;
const databasePassword = config.databasePassword;

export const pool = mysql.createPool({
	host: "127.0.0.1",
	user: databaseUser,
	password: databasePassword,
	database: "news_reports",
	waitForConnections: true,
	connectionLimit: 10,
	queueLimit: 0,
});
