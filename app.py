from flask import Flask, request, jsonify, make_response, abort
from db import Wall
import json
from decimal import Decimal

app = Flask(__name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def cors_middleware(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,X-Api-Key,baggage,sentry-trace'
    return response

@app.after_request
def after_request_func(response):
    return cors_middleware(response)

@app.route('/api/greet', methods=['GET', 'OPTIONS'])
def greet():
    if request.method == 'OPTIONS':
        return cors_middleware(make_response('', 204))
    response = {"status": "Connected"}
    return jsonify(response)

@app.route('/api/walls', methods=['POST'])
def addWall():
    print("Received")
    print("request", request)
    print("request", request.json)
    data = request.json
    print("Add wall", data)
    Wall.create(**data)
    response = {"message": "Wall added!"}
    return jsonify(response)

@app.route('/api/walls', methods=['GET', 'OPTIONS'])
def listWalls():
    if request.method == 'OPTIONS':
        return cors_middleware(make_response('', 204))
    walls_query = Wall.select()

    walls = [{
        'pair': wall_row.pair,
        'quantity': wall_row.quantity,
        'ask_price': wall_row.ask_price,
        'bid_price': wall_row.bid_price,
        'keep': wall_row.keep,
        'id': wall_row.id,
        'total': Decimal(wall_row.bid_price) * (Decimal(wall_row.quantity) + Decimal(wall_row.keep))

        } for wall_row in walls_query]
    return jsonify(walls)


if __name__ == '__main__':
    app.run(debug=True)
