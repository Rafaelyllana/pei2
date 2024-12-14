#!/usr/bin/env python

#       Programa: main.py
#       Propósito: Creación aplicación web Flask
#       Autor: Andres Pablo Rittmeyer

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/nivel1', methods=['GET'])
def author():
    author_name = os.getenv('AUTHOR_NAME')
    author_email = os.getenv('AUTHOR_EMAIL')

    if not author_name or not author_email:
        raise RuntimeError("Environment variables AUTHOR_NAME and AUTHOR_EMAIL are required")

    return jsonify({
        "author": author_name,
        "email": author_email
    })

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
