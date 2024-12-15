

#!/usr/bin/env python

#   Programa: main.py
#   Propósito: Creación aplicación web Flask
#   Autor: Andres Pablo Rittmeyer


import os
import uuid
import json
from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

# Configuración de Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

# Endpoint para crear un riesgo
@app.route('/risk/<city_id>', methods=['POST'])
def create_risk(city_id):
    try:
        data = request.get_json()
        city_name = data.get("city_name")
        risk = data.get("risk")
        level = data.get("level")

        # Validaciones
        if not city_name or not risk or not level:
            return jsonify({"error": "Missing fields"}), 400
        if len(risk) > 80:
            return jsonify({"error": "Risk description too long"}), 400
        if not isinstance(level, int) or level <= 0:
            return jsonify({"error": "Level must be a positive integer"}), 400

        # Persistir en Redis (expira en 10 segundos)
        risk_data = {
            "city_id": city_id,
            "city_name": city_name,
            "risk": risk,
            "level": level
        }
        redis_client.setex(city_id, 10, json.dumps(risk_data))

        return jsonify(risk_data), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para consultar un riesgo
@app.route('/risk/<city_id>', methods=['GET'])
def get_risk(city_id):
    try:
        risk_data = redis_client.get(city_id)
        if not risk_data:
            return jsonify({"error": "Risk not found"}), 404
        return jsonify(json.loads(risk_data)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)




























