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


# Download image from a URL
def download_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    input_layer = face_detection_compiled_model.input(0)
    height, width = image.shape[0:2]
    N, C, H, W = input_layer.shape
    resized_image = cv2.resize(image, (W, H))
    input_image = np.expand_dims(resized_image.transpose(2,0,1),0)
    return input_image, width, height

# Correctly resize and reshape the image
# Detect faces with OpenVINO
def detect_faces(image_url, compiled_model):
    image, width, height= download_image_from_url(image_url)
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
    # Download and preprocess the images
    image1, width1, height1 = download_image_from_url(image_url1)
    image2, width2, height2 = download_image_from_url(image_url2)

    # Detect faces in both images
    face1_box = detect_faces(image_url1, fd_compiled_model)
    face2_box = detect_faces(image_url2, fd_compiled_model)

    # Extract coordinates for cropping
    x1, y1, x2, y2 = face1_box.astype(int)
    x3, y3, x4, y4 = face2_box.astype(int)

    # Crop the faces from the images, ensuring correct dimension handling
    # Since these are color images, assume 3D with (Height, Width, Channels)
    cropped_face1 = image1[:, y1:y2, x1:x2]  # (Height, Width, Channels)
    cropped_face2 = image2[:, y3:y4, x3:x4]  # (Height, Width, Channels)

    # Adjusting for OpenVINO input requirements (needs batch size)
    batch_cropped_face1 = np.expand_dims(cropped_face1.transpose(2, 0, 1), axis=0)
    batch_cropped_face2 = np.expand_dims(cropped_face2.transpose(2, 0, 1), axis=0)

    # Generate face embeddings with reidentification model
    embedding1 = fr_compiled_model([batch_cropped_face1])[0]
    embedding2 = fr_compiled_model([batch_cropped_face2])[0]

    # Calculate similarity
    similarity = 1 - cosine(embedding1.flatten(), embedding2.flatten())

    return similarity






# Test with image URLs
matching_score = detect_and_compare_faces(
    "https://m.media-amazon.com/images/M/MV5BZjhkMzgzZGEtYjQ1Yi00NWUxLTk5NWMtNWY5MThjODRlMDczXkEyXkFqcGdeQXVyMTExNzQ3MzAw._V1_.jpg",
    "https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png",
    face_detection_compiled_model,
    face_reid_compiled_model
)

# print(f"Matching score between the two faces: {matching_score}")
image = download_image_from_url("https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png")

detect_faces("https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png", face_detection_compiled_model)
