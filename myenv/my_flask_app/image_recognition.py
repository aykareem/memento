import cv2
import numpy as np
import requests
from PIL import Image  # For image manipulation
import openvino as ov
from io import BytesIO

# OpenVINO Core
core = ov.Core()

# Load and compile the models
face_detection_model_path = "../intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml"
face_detection_compiled_model = core.compile_model(
    core.read_model(face_detection_model_path), "CPU"
)

face_reid_model_path = "../intel/face-reidentification-retail-0095/FP16/face-reidentification-retail-0095.xml"
face_reid_compiled_model = core.compile_model(
    core.read_model(face_reid_model_path), "CPU"
)

# Download image from a URL
def download_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

# Correctly resize and reshape the image
def correct_resizing(image, expected_shape):
    expected_height = expected_shape[2]
    expected_width = expected_shape[3]
    
    resized_image = cv2.resize(image, (expected_width, expected_height), interpolation=cv2.INTER_LINEAR)
    
    expected_size = np.prod(expected_shape[1:])
    
    resized_array = np.array(resized_image).astype(np.float32)
    
    if resized_array.size != expected_size:
        raise ValueError(f"Resized array size {resized_array.size} does not match expected {expected_size}")
    
    # Reshape to match the model's expected input shape
    reshaped_array = resized_array.reshape(1, 3, expected_height, expected_width)
    
    return reshaped_array

# Detect faces with OpenVINO
def detect_faces(image, compiled_model):
    input_blob = next(iter(compiled_model.inputs))
    expected_shape = compiled_model.input(input_blob.get_any_name()).shape
    
    image_data = correct_resizing(image, expected_shape)
    
    input_tensor = ov.Tensor(image_data)
    
    infer_request = compiled_model.create_infer_request()
    infer_request.set_input_tensor(input_tensor)
    infer_request.start_async()
    infer_request.wait()
    
    output = infer_request.get_output_tensor()
    output_data = output.data
    
    # Process face detection results
    faces = []
    for detection in output_data[0][0]:
        confidence = detection[2]
        if confidence > 0.071:
            xmin, ymin, xmax, ymax = detection[3:7]
            faces.append((xmin, ymin, xmax, ymax))
    
    return faces

# Detect and compare two faces
def detect_and_compare_faces(image_url1, image_url2, fd_compiled_model, fr_compiled_model):
    # Download and process both images
    image1 = download_image_from_url(image_url1)
    image2 = download_image_from_url(image_url2)
    
    # Detect faces in both images
    faces1 = detect_faces(image1, fd_compiled_model)
    faces2 = detect_faces(image2, fd_compiled_model)
    # Verify image dimensions and data type

    
    if not faces1 or not faces2:
        raise ValueError("Could not detect faces in one or both images")
    
    # Convert OpenCV to PIL for cropping
    pil_image1 = Image.fromarray(image1[:, :, ::-1])  # BGR to RGB
    pil_image2 = Image.fromarray(image2[:, :, ::-1])
    
    # Extract faces for re-identification
    face1 = pil_image1.crop(faces1[0])
    face2 = pil_image2.crop(faces2[0])
    
    print(face1.size, face1.mode)  # Check the size and mode of the image


    # Prepare data for re-identification
    face1_data = np.array(face1).transpose(2, 0, 1).astype(np.float32)  # Correct shape
    face2_data = np.array(face2).transpose(2, 0, 1).astype(np.float32)
    
    # Re-identification inference
    reid_input_blob = next(iter(fr_compiled_model.inputs))
    
    infer_request1 = fr_compiled_model.create_infer_request()
    infer_request1.set_input_tensor(ov.Tensor(face1_data))
    infer_request1.start_async()
    infer_request1.wait()
    reid_result1 = infer_request1.get_output_tensor().data
    
    infer_request2 = fr_compiled_model.create_infer_request()
    infer_request2.set_input_tensor(ov.Tensor(face2_data))
    infer_request2.start_async()
    infer_request2.wait()
    reid_result2 = infer_request2.get_output_tensor().data

    matching_score = np.dot(reid_result1.flatten(), reid_result2.flatten())
    return matching_score  # Return the score





# Test with image URLs
matching_score = detect_and_compare_faces(
    "https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/LeBron_James_%2851959977144%29_%28cropped2%29.jpg/640px-LeBron_James_%2851959977144%29_%28cropped2%29.jpg",
    face_detection_compiled_model,
    face_reid_compiled_model
)

# print(f"Matching score between the two faces: {matching_score}")
image = download_image_from_url("https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/1966.png")

