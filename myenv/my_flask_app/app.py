from flask import Flask, request, jsonify
import data_manager as dm
import image_recognition as ir

app = Flask(__name__)

# Endpoint to get all profiles (for testing purposes)
@app.route('/profiles', methods=['GET'])
def get_profiles():
    # Return the list of profiles
    return jsonify({'profiles': [p.__dict__ for p in dm.profiles]})

# Endpoint to add a new profile
@app.route('/add-profile', methods=['POST'])
def add_profile():
    data = request.get_json()  # Get the JSON data
    name = data.get('name')
    picture = data.get('picture')  # URL or image reference
    
    if not name or not picture:
        return jsonify({'error': 'Name and picture are required'}), 400

    # Add the new profile using data_manager
    new_profile = dm.add_profile(name, picture)
    return jsonify({'status': 'Profile added', 'profile': new_profile.__dict__}), 201

# Endpoint for image scanning
@app.route('/scan', methods=['POST'])
def scan_image():
    data = request.get_json()  # Get JSON data
    image_url = data.get('image_url')  # Assuming image URL is provided
    
    if not image_url:
        return jsonify({'error': 'Image URL is required'}), 400

    # Match the image against profiles
    match_result = dm.match(image_url)
    
    return jsonify({
        'status': 'success',
        'matched_name': match_result[0],  # Matched profile name
        'relation': match_result[1],  # Matched profile relation
    })

# Flask server setup
if __name__ == '__main__':
    # Start the server on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
