from flask import Flask, request, jsonify

mock_app = Flask(__name__)

@mock_app.route('/test', methods=['GET', 'POST', 'PUT', 'DELETE'])
def test_route():
    response = {
        'method': request.method,
        'headers': dict(request.headers),
        'data': request.get_json(silent=True) or request.form.to_dict() or request.data.decode('utf-8')
    }
    return jsonify(response), 200

@mock_app.route('/error', methods=['GET'])
def error_route():
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    mock_app.run(port=8080, debug=True)