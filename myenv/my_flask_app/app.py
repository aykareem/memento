from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask server"})

@app.route('/receive-data', methods=['POST'])
def receive_data():
    # Get data from the request
    data = request.json  # Assuming the data is in JSON format
    # Process the data (you can perform any operation or logic here)
    print(data)  # For debugging/validation
    
    # Create a response
    response = {
        "status": "success",
        "received_data": data
    }
    return jsonify(response), 200  # Return a JSON response with a 200 status


if __name__ == '__main__':
    app.run(debug=True)
