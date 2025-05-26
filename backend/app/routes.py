from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "GeoportalSV API está funcionando correctamente"})
