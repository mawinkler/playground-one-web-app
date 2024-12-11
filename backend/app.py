from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'message': 'Hello from Flask!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
