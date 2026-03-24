from flask import Blueprint
from src.models.ticket import Ticket
from src.routes.routes_base import create_response

ticket_bp = Blueprint('tickets', __name__)

@ticket_bp.route('/tickets', methods=['GET'])
def get_tickets():
    tickets = Ticket.find_all()
    data = [{"ticket_code": t.ticket_code, "name": t.name} for t in tickets]
    return create_response({"ok": True, "data": data}), 200
