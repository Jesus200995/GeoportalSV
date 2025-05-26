from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexiones desde tu frontend en Vue

@app.route('/')
def index():
    return jsonify({"message": "Backend del Geoportal funcionando correctamente"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
