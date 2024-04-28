from flask import Flask, request, jsonify
import data_manager as dm  # Updated module for managing profiles

# Initialize Flask application
app = Flask(__name__)

# Endpoint to scan an image and return the best matching profile name
@app.route('/scan', methods=['POST'])
def scan_image():
    data = request.get_json()  # Get JSON data from the request
    image_url = data.get('image_url')  # The image URL to scan

    if not image_url:
        return jsonify({'error': 'Image URL is required'}), 400  # Return error if no URL is provided

    # Match the image against profiles and get the best match name
    matched_name = dm.match(image_url)  # Updated logic to handle multiple pictures per person

    if not matched_name:
        return jsonify({'error': 'No match found'}), 404  # Return error if no match is found

    # Return the matched name as JSON
    return jsonify({'matched_name': matched_name}), 200

# Flask server setup
if __name__ == '__main__':
    # Start the Flask server on all network interfaces
    app.run(host='0.0.0.0', port=5001, debug=True)
