import requests  # For downloading images from URLs
from PIL import Image  # For image manipulation
from io import BytesIO  # To convert bytes to image
import openvino as ov
import numpy as np


ie = ov.Core()


face_detection_model_path = "../intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml"
model = ie.read_model(model=face_detection_model_path)
compiled_model = ie.compile_model(model, "CPU")


# Load the face re-identification model
face_reid_model_path = "../intel/face-reidentification-retail-0095/FP16/face-reidentification-retail-0095.xml"
model = ie.read_model(model=face_reid_model_path)
compiled_model = ie.compile_model(model, "CPU")

def detect_faces(image):
    # Convert the image to a compatible format
    image_data = np.array(image).transpose(2, 0, 1)  # Transpose for OpenVINO
    input_blob = list(face_detection_exec_net.input_info.keys())[0]  # Get input blob
    
    # Run the face detection inference
    face_detection_result = face_detection_exec_net.infer({input_blob: [image_data]})
    
    # Process the results to extract bounding boxes
    faces = []
    for detection in face_detection_result.items():
        for det in detection[1][0]:
            confidence = det[2]
            if confidence > 0.5:  # Confidence threshold
                xmin, ymin, xmax, ymax = det[3:7]
                faces.append((xmin, ymin, xmax, ymax))
    
    return faces  # Return list of detected face bounding boxes


# Function to detect and compare two faces from two images
def detect_and_compare_faces(image1, image2):
    # Detect faces in both images
    faces1 = detect_faces(image1)
    faces2 = detect_faces(image2)
    
    # Ensure at least one face is detected in each image
    if not faces1 or not faces2:
        raise ValueError("Could not detect faces in one or both images")
    
    # Extract the first detected face from each image
    face1 = image1.crop((faces1[0][0], faces1[0][1], faces1[0][2], faces1[0][3]))  # Extract using bounding box
    face2 = image2.crop((faces2[0][0], faces2[0][1], faces2[0][2], faces2[0][3]))
    
    # Prepare the faces for re-identification
    face1_data = np.array(face1).transpose(2, 0, 1)  # Prepare data for inference
    face2_data = np.array(face2).transpose(2, 0, 1)
    
    # Get input blob for re-identification
    reid_input_blob = list(face_reid_exec_net.input_info.keys())[0]
    
    # Run re-identification on both faces
    reid_result1 = face_reid_exec_net.infer({reid_input_blob: [face1_data]})
    reid_result2 = face_reid_exec_net.infer({reid_input_blob: [face2_data]})
    
    # Compute a matching score (example logic)
    matching_score = np.dot(reid_result1["output_blob"], reid_result2["output_blob"])
    
    return matching_score  # Return the matching score between two faces
