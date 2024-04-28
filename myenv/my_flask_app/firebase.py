import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def initialize_firebase(json_path):
    """Initialize Firebase with a service account JSON."""
    cred = credentials.Certificate(json_path)
    firebase_admin.initialize_app(cred)

def setup_firestore_listener(collection_name):
    """Set up a Firestore listener that returns a dictionary with names and image URLs."""
    db = firestore.client()
    contacts_photos_dict = {}  # Dictionary to hold names and image URLs

    # Callback function for snapshot events
    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            doc = change.document.to_dict()
            name = doc.get("name", "Unknown")
            photo_urls = doc.get("photoURLs", [])
            photo_url = photo_urls[0] if photo_urls else "No photo"

            if change.type.name in ("ADDED", "MODIFIED"):
                contacts_photos_dict[name] = photo_url
            elif change.type.name == "REMOVED":
                contacts_photos_dict.pop(name, None)

    # Attach the listener to the specified collection
    col_reference = db.collection(collection_name)
    col_watch = col_reference.on_snapshot(on_snapshot)

    # Function to stop the listener
    def stop_listener():
        col_watch.unsubscribe()
        return contacts_photos_dict

    return contacts_photos_dict, stop_listener


# Main execution for testing
if __name__ == "__main__":
    # Initialize Firebase and set up Firestore listener
    json_path = r'/Users/raramand/Desktop/memento/myenv/momento-49924-firebase-adminsdk-u0bz9-1e3ca43fe0.json'  # Path to your Firebase service account JSON
    collection_name = 'contacts'  # Collection to listen to

    # Initialize Firebase and start the listener
    initialize_firebase(json_path)
    contacts_photos_dict, stop_listener = setup_firestore_listener(collection_name)

    print("Listening for Firestore changes... Press Enter to stop.")
    input()  # Keep the program running to listen for changes

    # Stop the listener and display the final state of the dictionary
    contacts_photos_dict = stop_listener()
    print("Stopped listening. Final state of contacts photos dictionary:")
    print(contacts_photos_dict)



