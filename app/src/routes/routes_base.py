from flask import jsonify

def create_response(r):
	response = {
		"status": "Success" if r.get("ok") else "Error",
		"message": r.get("msg") or "",
		"data": r.get("data") or None
	}
	return jsonify(response)