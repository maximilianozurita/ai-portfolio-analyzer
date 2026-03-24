CREATE DATABASE IF NOT EXISTS stats;
USE stats;

CREATE TABLE IF NOT EXISTS tickets (
	ticket_code varchar(50) PRIMARY KEY UNIQUE,
	name varchar(50) not null,
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

CREATE TABLE IF NOT EXISTS bond_holding (
	id            INT AUTO_INCREMENT PRIMARY KEY UNIQUE NOT NULL,
	bond_code     VARCHAR(20) NOT NULL UNIQUE,
	quantity      INT NOT NULL,
	ppc           FLOAT NOT NULL,
	ppc_paridad   FLOAT NOT NULL,
	weighted_date BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS bond_transaction (
	id                    INT AUTO_INCREMENT PRIMARY KEY UNIQUE,
	bond_code             VARCHAR(20) NOT NULL,
	transaction_type      ENUM('compra','venta','cupon','amortizacion') NOT NULL,
	quantity              INT NOT NULL,
	unit_price            FLOAT NOT NULL,
	valor_tecnico         FLOAT NOT NULL,
	interest_currency     ENUM('ARS','USD') NOT NULL,
	amortization_currency ENUM('ARS','USD') NOT NULL,
	usd_quote             INT NOT NULL,
	date                  BIGINT NOT NULL,
	broker_name           VARCHAR(50),
	transaction_key       INT
);
