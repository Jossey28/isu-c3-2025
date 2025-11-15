import { pool } from "../db";

export default defineEventHandler(async (event) => {
	const query = getQuery(event);

	let sql = "SELECT * FROM articles";
	const params: any[] = [];

	if (query.id) {
		sql += " WHERE id = ?";
		params.push(query.id);
	} else if (query.category) {
		sql += " WHERE category = ?";
		params.push(query.category);
	}

	try {
		const [rows] = await pool.query(sql, params);
		return rows;
	} catch (err) {
		console.error(err);
		throw createError({
			statusCode: 500,
			statusMessage: "Failed to fetch articles",
		});
	}
});
