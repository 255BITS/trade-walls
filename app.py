from flask import Flask, request, jsonify, make_response, abort
from db import Wall

app = Flask(__name__)

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

@app.route('/api/addWall', methods=['POST'])
def addWall():
    Wall.create(type="buy", price="0.01", pair="ETH/NEAR", min_holdings=10, quantity=10)
    response = {"message": "Wall added!"}
    return jsonify(response)

@app.route('/api/walls', methods=['GET', 'OPTIONS'])
def listWalls():
    if request.method == 'OPTIONS':
        return cors_middleware(make_response('', 204))
    walls_query = Wall.select()

    walls = [{
        'pair': 'ETH/NEAR',
        'quantity': 100,
        'sell_price': 2,
        'buy_price': 1,
        'id': wall_row.id


        } for wall_row in walls_query]
    return jsonify(walls)


if __name__ == '__main__':
    app.run(debug=True)
