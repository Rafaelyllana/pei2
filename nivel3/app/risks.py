#   Programa: main.py
#   Propósito: Creación aplicación web Flask
#   Autor: Andres Pablo Rittmeyer

from flask import request, jsonify
import memorystore
import uuid
import json
import cloudstorage


def register_routes(app):
    @app.route('/risk/<risk_id>', methods=['GET', 'POST'])
    def risk_handler(risk_id):
        """
        Handler for GET and POST requests for risk management.
        """
        if request.method == 'GET':
            try:
                # Nivel 3 y 4: Consulta en Redis (in-memory DB)
                risk = memorystore.load(uuid.UUID(risk_id))
                if risk:
                    return jsonify({"cache": True, **risk}), 200

                # Nivel 5: Buscar en GCP Storage si no está en Redis
                try:
                    blob_data = cloudstorage.download_blob(risk_id)
                    risk = json.loads(blob_data)
                    # Añadir de nuevo a Redis como caché
                    memorystore.save_risk(risk_id=uuid.UUID(risk_id), **risk)
                    return jsonify({"cache": False, **risk}), 200
                except Exception:
                    return jsonify({"error": "Risk not found"}), 404
            except Exception as e:
                return jsonify({"error": f"Unexpected error: {e}"}), 500

        if request.method == 'POST':
            try:
                data = request.get_json()
                # Validación de los parámetros
                assert "risk" in data, "missing risk parameter"
                assert len(data["risk"]) <= 80, "risk must be less than 80 characters"
                assert "level" in data, "missing level parameter"
                assert isinstance(data["level"], int), "level must be an integer"
                assert "city_name" in data, "missing city_name parameter"
                assert len(data["city_name"]) <= 180, "city_name must be less than 180 characters"

                # Si no se especifica un `risk_id`, generar uno nuevo
                risk_id = uuid.UUID(risk_id)
                risk = add_risk(risk_id=risk_id, **data)
                return jsonify(risk), 201
            except AssertionError as e:
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                return jsonify({"error": f"Unexpected error: {e}"}), 500


def add_risk(risk_id: uuid.UUID, **risk_description):
    """
    Add a risk to the in-memory database and optionally GCP Storage.
    """
    try:
        # Nivel 3 y 4: Guardar en Redis (in-memory DB)
        risk = memorystore.save_risk(risk_id=risk_id, **risk_description)

        # Nivel 5: Guardar en GCP Storage como respaldo
        try:
            cloudstorage.upload_blob(blob_name=str(risk_id), blob_data=json.dumps(risk_description))
        except Exception as e:
            print(f"Warning: Failed to store risk in GCP Storage: {e}")

        return risk
    except Exception as e:
        raise RuntimeError(f"Failed to add risk: {e}")
