CREATE DATABASE IF NOT EXISTS stats;
USE stats;

CREATE TABLE IF NOT EXISTS tickets (
	ticket_code varchar(50) PRIMARY KEY UNIQUE,
	name varchar(50) not null,
	ratio INT,
	date BIGINT
);

CREATE TABLE IF NOT EXISTS stock (
	id INT AUTO_INCREMENT PRIMARY KEY UNIQUE not null,
	ticket_code varchar(50) not null UNIQUE,
	ppc FLOAT not null,
	quantity INT not null,
	weighted_date BIGINT not null,
	FOREIGN KEY (ticket_code) REFERENCES tickets(ticket_code)
);

CREATE TABLE IF NOT EXISTS transaction (
	id INT AUTO_INCREMENT PRIMARY KEY UNIQUE,
	ticket_code varchar(50) not null,
	ratio INT,
	transaction_key INT,
	broker_name varchar(50),
	quantity INT not null,
	unit_price FLOAT not null,
	usd_quote INT not null,
	date BIGINT not null,
	FOREIGN KEY (ticket_code) REFERENCES tickets(ticket_code)
);

CREATE TABLE IF NOT EXISTS tokens (
	id INT PRIMARY KEY UNIQUE,
	access_token TEXT not null,
	refresh_token TEXT not null,
	token_expires BIGINT not null,
	refresh_expires BIGINT not null
);
