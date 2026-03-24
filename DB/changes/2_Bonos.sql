USE stats;

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
