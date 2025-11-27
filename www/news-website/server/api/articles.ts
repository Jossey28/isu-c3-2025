import { pool } from "../db";

export default defineEventHandler(async (event) => {
	const query = getQuery(event);

	if (!query.id && !query.category) {
	throw createError({
	  statusCode: 400,
	  statusMessage: "Invalid query parameters provided",
	});
  }

	let sql = "";
	const params: any[] = [];

	if (query.id) {
		sql += "SELECT * FROM articles WHERE id = ?";
		params.push(query.id);
	} else if (query.category) {
		sql += "SELECT * FROM articles WHERE category = ?";
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
