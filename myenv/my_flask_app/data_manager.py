import image_recognition as ir
import firebase
import numpy as np  # For averaging
from firebase import setup_firestore_listener, initialize_firebase
import time

# Initialize Firebase
json_path = '/Users/raramand/Desktop/memento/myenv/momento-49924-firebase-adminsdk-u0bz9-1e3ca43fe0.json'  # Path to your Firebase service account JSON
collection_name = 'contacts'  # Collection to listen to

# Initialize Firebase and set up Firestore listener
initialize_firebase(json_path)
contacts_photos_dict, stop_listener = setup_firestore_listener(collection_name)
time.sleep(5)
# Function to find the best match by averaging matching scores
def match(image_url: str):
    if not contacts_photos_dict:
        print("No profiles in Firestore")
        return None
    
    max_avg_score = 0  # Track the highest average matching score
    best_match = None  # Store the name of the best match

    # Loop through each person in the dictionary
    for name, photo_urls in contacts_photos_dict.items():
        # Calculate matching scores for all image URLs
        matching_scores = [ir.detect_and_compare_faces(image_url, url, ir.face_detection_compiled_model, ir.face_reid_compiled_model) for url in photo_urls]
        
        # Calculate the average matching score
        avg_score = np.mean(matching_scores)  # Using numpy for mean
        
        # Update the best match if the current average score is higher
        if avg_score > max_avg_score:
            max_avg_score = avg_score
            best_match = name
    
    return best_match  # Return the name of the best match


# Testing the matching function
if __name__ == "__main__":
    # Example URL to scan
    test_image_url = 'https://firebasestorage.googleapis.com:443/v0/b/momento-49924.appspot.com/o/images%2FC73ECC6B-48E0-4B92-B3DD-2ABAA465F3BB.jpg?alt=media&token=817aa7a9-95d1-4a9a-ac21-80d371451fb1'
    
    best_match = match(test_image_url)
    if best_match:
        print(f"The best match is: {best_match}")
    else:
        print("No match found")


