from flask import Flask, request, jsonify
import data_manager as dm  # Import the module for managing profiles

# Initialize Flask application
app = Flask(__name__)

# Endpoint for image scanning
@app.route('/scan', methods=['POST'])
def scan_image():
    # Retrieve JSON data from the request
    data = request.get_json()
    image_url = data.get('image_url')  # Get the image URL from the request
    
    if not image_url:
        return jsonify({'error': 'Image URL is required'}), 400
    
    # Match the image against profiles to get the best match name
    matched_name = dm.match(image_url)
    
    if not matched_name:
        return jsonify({'error': 'No match found'}), 404  # Return error if no match is found
    
    # Return the matched name as JSON
    return jsonify({'matched_name': matched_name}), 200

# Flask server setup
if __name__ == '__main__':
    # Start the Flask server on all network interfaces
    app.run(host='0.0.0.0', port=5001, debug=True)  # Start the server on port 5001
