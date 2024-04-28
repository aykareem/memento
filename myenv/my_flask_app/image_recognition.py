import cv2
import numpy as np
import requests
from PIL import Image  # For image manipulation
import openvino as ov
from io import BytesIO


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
    # Download and process both images
    image1, image1_w, image1_h = download_image_from_url(image_url1)
    image2, image2_w, image2_h = download_image_from_url(image_url2)
    new_image1 = np.squeeze(image1)
    new_image2 = np.squeeze(image2)
    new_image1 = image1.transpose(1, 2, 0)
    new_image2 = image2.transpose(1, 2, 0)

    image1_rgb = new_image1[:, :, ::-1]
    image2_rgb = new_image2[:, :, ::-1]

    
    # Detect faces in both images
    faces1 = detect_faces(image_url1, fd_compiled_model)
    faces2 = detect_faces(image_url2, fd_compiled_model)
    # Verify image dimensions and data type

    
    #if not faces1 or not faces2:
        #raise ValueError("Could not detect faces in one or both images")
    
    # Convert OpenCV to PIL for cropping
    # Check the shape and data type
    print("Shape of image1:", image1.shape)
    print("Data type of image1:", image1.dtype)

    pil_image1 = Image.fromarray(image1_rgb)
    pil_image2 = Image.fromarray(image2_rgb)

    
    print(pil_image1.size, pil_image1.mode)

    # Extract faces for re-identification
    print(faces1[0])
    face1 = pil_image1.crop(faces1)
    face2 = pil_image2.crop(faces2)
    
    print(face1.size, face1.mode)  # Check the size and mode of the image


    # Prepare data for re-identification
    #face1_data = np.array(face1).transpose(2, 0, 1).astype(np.float32)  # Correct shape
    #face2_data = np.array(face2).transpose(2, 0, 1).astype(np.float32)
    
    # Re-identification inference
    reid_input_blob = next(iter(fr_compiled_model.inputs))
    
    infer_request1 = fr_compiled_model.create_infer_request()
    infer_request1.set_input_tensor(ov.Tensor(face1))
    infer_request1.start_async()
    infer_request1.wait()
    reid_result1 = infer_request1.get_output_tensor().data
    
    infer_request2 = fr_compiled_model.create_infer_request()
    infer_request2.set_input_tensor(ov.Tensor(face2))
    infer_request2.start_async()
    infer_request2.wait()
    reid_result2 = infer_request2.get_output_tensor().data

    matching_score = np.dot(reid_result1.flatten(), reid_result2.flatten())
    return matching_score  # Return the score





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
