import time

# Initialize Firebase and set up Firestore listener
import firebase
import image_recognition as ir
json_path = r'/Users/raramand/Desktop/memento/myenv/momento-49924-firebase-adminsdk-u0bz9-1e3ca43fe0.json'
collection_name = 'contacts'

# Initialize Firebase and setup Firestore listener
firebase.initialize_firebase(json_path)
contacts_photos_dict, stop_listener = firebase.setup_firestore_listener(collection_name)

# Allow some time for Firestore to populate
time.sleep(5)  # Adjust based on your setup and network speed
#print(contacts_photos_dict)
# Example function to use the dictionary for matching
def match(image: str):
    if not contacts_photos_dict:
        print("No profiles in Firestore")
        return None
    
    max_name = None
    max_score = 0.15
    for name, picture in contacts_photos_dict.items():
        matching_score = ir.detect_and_compare_faces(image, picture, ir.face_detection_compiled_model, ir.face_reid_compiled_model)
        if matching_score > max_score:
            max_score = matching_score
            max_name = name
    
    return max_name

name = match("https://firebasestorage.googleapis.com:443/v0/b/momento-49924.appspot.com/o/images%2F1742D33C-4D6B-401F-9FF7-A27A430188EF.jpg?alt=media&token=6c817dcd-914b-4406-8027-1c78835a884d")
print(name)

