from flask import Flask, jsonify
from . import unique_number_generator as ung

ung.create_new_connection()

app = Flask(__name__)

@app.route('/getnumber', methods=['GET'])
def unique_number_generator():
    return jsonify({"message": f"ung.generate_unique_tracking_number()"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
