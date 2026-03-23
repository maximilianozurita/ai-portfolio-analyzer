USE stats;
INSERT INTO tickets (ticket_code, name, ratio, date) VALUES
    ('AAPL', 'Apple', 10, UNIX_TIMESTAMP()),
    ('AMD', 'Amd', 10, UNIX_TIMESTAMP()),
    ('BRKB', 'Berkshire Hathaway', 22, UNIX_TIMESTAMP()),
    ('DISN', 'Disney', 12, UNIX_TIMESTAMP()),
    ('GOOGL', 'Google', 58, UNIX_TIMESTAMP()),
    ('INTC', 'Intel', 5, UNIX_TIMESTAMP()),
    ('JPM', 'Jpmorgan Chase & Co.', 5, UNIX_TIMESTAMP()),
    ('KO', 'Coca cola', 5, UNIX_TIMESTAMP()),
    ('MA', 'Mastercard', 33, UNIX_TIMESTAMP()),
    ('MCD', 'Mac Donalds', 24, UNIX_TIMESTAMP()),
    ('MELI', 'Mercado libre', 60, UNIX_TIMESTAMP()),
    ('META', 'Meta', 24, UNIX_TIMESTAMP()),
    ('MSFT', 'Microsoft', 30, UNIX_TIMESTAMP()),
    ('NVDA', 'Nvidia', 24, UNIX_TIMESTAMP()),
    ('PBR', 'Petrobras', 1, UNIX_TIMESTAMP()),
    ('PEP', 'Pepsico', 6, UNIX_TIMESTAMP()),
    ('V', 'Visa', 18, UNIX_TIMESTAMP()),
    ('VIST', 'Vista', 1, UNIX_TIMESTAMP()),
    ('WMT', 'Wallmart', 6, UNIX_TIMESTAMP()),
    ('PAMP', 'Pampa', 1, UNIX_TIMESTAMP()),
    ('YPF', 'Ypf', 1, UNIX_TIMESTAMP())
ON DUPLICATE KEY UPDATE name=VALUES(name), ratio=VALUES(ratio), date=VALUES(date);
