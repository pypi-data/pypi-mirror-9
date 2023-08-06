CREATE TABLE experiment(
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	name varchar not null,
	description varchar not null,
	check(length(name) >= 4 and length(name) <= 8)
);
