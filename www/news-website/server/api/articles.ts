import { pool } from "../db";

export default defineEventHandler(async (event) => {
	const query = getQuery(event);

	if (event.node.req.method !== "GET") {
		throw createError({
			statusCode: 405,
			statusMessage: "Method not allowed",
		});
	}

	if (!query.id && !query.category) {
	throw createError({
	  statusCode: 400,
	  statusMessage: "Invalid query parameters provided",
	});
  }

	let sql = "";
	const params: (string | number)[] = [];

	if (query.id) {

		if (isNaN(Number(query.id)) && typeof query.id !== "number") {
			throw createError({
				statusCode: 400,
				statusMessage: "Article ID must be a number",
			});
		}

		sql += "SELECT * FROM articles WHERE id = ?";
		params.push(query.id);
	} else if (query.category) {

		if (typeof query.category !== "string") {
			throw createError({
				statusCode: 400,
				statusMessage: "Category must be a string",
			});
		}

		sql += "SELECT * FROM articles WHERE category = ?";
		params.push(query.category);
	}

	try {
		const [rows] = await pool.query(sql, params);
		return rows;
	} catch (err) {
		console.error("	Error fetching articles:");
		throw createError({
			statusCode: 500,
			statusMessage: "Failed to fetch articles",
		});
	}
});
