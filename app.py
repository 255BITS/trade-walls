from flask import Flask, request, jsonify, make_response, abort
from db import Wall
import json
from decimal import Decimal
from trade_agent import get_market_trade_history
from walls import Walls

app = Flask(__name__)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def cors_middleware(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE, PUT'
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

@app.route('/api/walls/<int:wall_id>', methods=['PUT'])
def updateWall(wall_id):
    data = request.json
    wall = Wall.get_by_id(wall_id)
    if wall:
        wall.pair = data['pair']
        wall.quantity = data['quantity']
        wall.ask_price = data['ask_price']
        wall.bid_price = data['bid_price']
        wall.keep = data['keep']
        wall.save()
        response = {"message": "Wall updated!"}
    else:
        response = {"message": "Wall not found!"}
    return jsonify(response)

@app.route('/api/walls/<int:wall_id>', methods=['DELETE'])
def deleteWall(wall_id):
    if request.method == 'OPTIONS':
        return cors_middleware(make_response('', 204))
    wall = Wall.get_by_id(wall_id)
    for h in wall.executions:
        h.delete_instance()
    if wall:
        wall.delete_instance()
        response = {"message": "Wall deleted!"}
    else:
        response = {"message": "Wall not found!"}
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
    status = "TODO"

    walls = []
    for db_wall in walls_query:
        wall = Walls(pair=db_wall.pair, bid_price=Decimal(db_wall.bid_price), ask_price=Decimal(db_wall.ask_price), keep=Decimal(db_wall.keep), quantities=[Decimal(db_wall.quantity)])
        wall.print()
        history = get_market_trade_history(db_wall)
        print("WALL", wall.keep, wall.potential_spend(history))
        walls += [{
            'pair': db_wall.pair,
            'quantity': db_wall.quantity,
            'ask_price': db_wall.ask_price,
            'bid_price': db_wall.bid_price,
            'keep': db_wall.keep,
            'id': db_wall.id,
            'status': wall.status(history)
        }]
    return jsonify(walls)


if __name__ == '__main__':
    app.run(debug=True)
