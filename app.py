from flask import Flask, request, jsonify, make_response, abort

app = Flask(__name__)

API_KEY = 'your_api_key_here'  # The secret API key

#@app.before_request
#def api_auth():
#    if request.method == 'OPTIONS':
#        return
#    api_key = request.headers.get('X-Api-Key')
#    if not api_key or api_key != API_KEY:
#        abort(401)

def cors_middleware(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,X-Api-Key'
    return response

@app.after_request
def after_request_func(response):
    return cors_middleware(response)

@app.route('/api/greet', methods=['GET', 'OPTIONS'])
def greet():
    if request.method == 'OPTIONS':
        return cors_middleware(make_response('', 204))
    response = {"message": "Ahoy from Flask with CORS and API Key!"}
    return jsonify(response)

@app.route('/api/addWall', methods=['POST'])
def addWall():
    response = {"message": "Wall added!"}
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
