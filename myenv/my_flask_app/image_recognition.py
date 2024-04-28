import cv2
import numpy as np
import requests
from PIL import Image  # For image manipulation
import openvino as ov
from io import BytesIO
from scipy.spatial.distance import cosine



# OpenVINO Core
core = ov.Core()

# Load and compile the models
face_detection_model_path = "../intel/face-detection-adas-0001/FP32/face-detection-adas-0001.xml"
face_detection_model = core.read_model(model = face_detection_model_path)
face_detection_compiled_model = core.compile_model(model = face_detection_model, device_name= "CPU")

input_layer_ir = face_detection_compiled_model.input(0)
output_layer_ir = face_detection_compiled_model.output(0)

face_reid_model_path = "../intel/face-reidentification-retail-0095/FP32/face-reidentification-retail-0095.xml"
face_reid_model = core.read_model(model = face_reid_model_path)
face_reid_compiled_model = core.compile_model(model = face_reid_model, device_name = "CPU")

# Validate and correct the URL if needed
def validate_url(url):
    if not (url.startswith("http://") or url.startswith("https://")):
        # If there's no schema, prepend "https://" by default
        url = "https://" + url
    return url

# Example usage with corrected URL
def download_image_from_url(url):
    corrected_url = validate_url(url)  # Ensure the URL has the correct schema
    response = requests.get(corrected_url)  # Send a GET request to download the image
    response.raise_for_status()  # Check if the request was successful
    return response.content  # Return the raw content of the response


# Download image from a URL
def download_image_from_url(url):
    response = requests.get(url)  # Send a GET request to download the image
    response.raise_for_status()  # Ensure the download was successful
    
    # Convert the response content to a numpy array and decode into an OpenCV image
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # Read as a color image
    
    # Get the expected input shape for your model
    input_layer = face_detection_compiled_model.input(0)
    N, C, H, W = input_layer.shape  # The expected shape (batch, channels, height, width)
    
    # Resize the image to fit the model's expected shape
    resized_image = cv2.resize(image, (W, H))  # Resize to the expected dimensions
    
    # Adjust the shape to match the model's input requirements (transpose and add batch dimension)
    input_image = np.expand_dims(resized_image.transpose(2, 0, 1), 0)  # (1, channels, height, width)
    
    # Get the width and height of the original image
    height, width = image.shape[:2]

    return input_image, width, height, image

# Correctly resize and reshape the image
# Detect faces with OpenVINO
def detect_faces(image_url, compiled_model):
    image, width, height, blank= download_image_from_url(image_url)
    THRESH = 0.3
    boxes = compiled_model([image])[output_layer_ir]
    boxes=boxes.squeeze()[:,-5:]
    boxes=np.array([x[-4:] for x in boxes if x[0]>THRESH])
    boxes = boxes*np.array([width, height, width, height])
    for box in boxes:
        print(box)
        return box

# Detect and compare two faces
def detect_and_compare_faces(image_url1, image_url2, fd_compiled_model, fr_compiled_model):
    new_image1, width1, height1, image1 = download_image_from_url(image_url1)
    new_image2, width2, height2, image2 = download_image_from_url(image_url2)
    # Detect faces in both images
    face1_box = detect_faces(image_url1, face_detection_compiled_model)
    face2_box = detect_faces(image_url2, face_detection_compiled_model)

    # Extract coordinates for cropping
    x1, y1, x2, y2 = face1_box.astype(int)
    x3, y3, x4, y4 = face2_box.astype(int)

    # Crop the faces from the images
    face1 = image1[y1:y2, x1:x2]  # Adjusted shape for OpenVINO model input
    face2 = image2[y3:y4, x3:x4]  # Adjusted shape for OpenVINO model input
    #print(face1.size)
    #print(face2.size)

    # Resize the faces to 128x128
    resized_face1 = cv2.resize(face1, (128, 128))
    resized_face2 = cv2.resize(face2, (128, 128))
    

    # Add a batch dimension and transpose to match expected shape
    tensor_face1 = np.expand_dims(resized_face1.transpose(2, 0, 1), axis=0)
    tensor_face2 = np.expand_dims(resized_face2.transpose(2, 0, 1), axis=0)


    embedding1 = fr_compiled_model([tensor_face1])[0]
    embedding2 = fr_compiled_model([tensor_face2])[0]

    similarity = 1 - cosine(embedding1.flatten(), embedding2.flatten())


    return similarity





# Test with image URLs
matching_score = detect_and_compare_faces(
    "https://firebasestorage.googleapis.com/v0/b/momento-49924.appspot.com/o/images%2FA341E669-2A16-4D8F-9EA3-C5A5D40FB111.jpg?alt=media&token=875033fb-26eb-42df-86a6-3eab135f2643",
    "https://firebasestorage.googleapis.com/v0/b/momento-49924.appspot.com/o/images%2F75138553-7570-46B2-96B1-71B70830C41C.jpg?alt=media&token=dc97232a-0ce9-4ca6-9f54-235abf3f9869",
    face_detection_compiled_model,
    face_reid_compiled_model
)
print("matching score is", matching_score)

# print(f"Matching score between the two faces: {matching_score}")
image = download_image_from_url("https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png")

detect_faces("https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png", face_detection_compiled_model)
