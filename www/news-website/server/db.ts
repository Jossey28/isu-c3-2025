import mysql from "mysql2/promise";

export const pool = mysql.createPool({
	host: "127.0.0.1",
	user: "nuxt",
	password: "cdc",
	database: "news_reports",
	waitForConnections: true,
	connectionLimit: 10,
	queueLimit: 0,
});
