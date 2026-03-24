from flask import Flask
from flask_cors import CORS
from src.routes.stocks import stock as stocks_bp
from src.routes.transactions import stock as transactions_bp
from src.routes.tickets import ticket_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(stocks_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(ticket_bp)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)
