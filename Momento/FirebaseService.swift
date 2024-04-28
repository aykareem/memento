import Firebase
import FirebaseStorage
import FirebaseFirestore
import UIKit

class FirebaseService {
    static let shared = FirebaseService()
    private let db = Firestore.firestore()
    private let storage = Storage.storage().reference()
    
    func createContactWithImages(name: String, relation: String, occupation: String, city: String, dateOfBirth: String, images: [UIImage], completion: @escaping (Error?) -> Void) {
        // First, upload the images
        uploadImages(images: images) { result in
            switch result {
            case .success(let urls):
                // Once all images are uploaded and we have their URLs, create the contact
                let newContact = Contact(
                    id: UUID().uuidString,
                    name: name,
                    relation: relation,
                    occupation: occupation,
                    city: city,
                    dateOfBirth: dateOfBirth,
                    photoURLs: urls
                )
                
                // Add the contact to Firestore
                self.addContact(contact: newContact, completion: completion)
                
            case .failure(let error):
                completion(error)
            }
        }
    }
    
    // Upload a single image to Firebase Storage
    func uploadImage(image: UIImage, completion: @escaping (Result<String, Error>) -> Void) {
        guard let imageData = image.jpegData(compressionQuality: 0.75) else {
            completion(.failure(FirebaseError.imageConversionFailed))
            return
        }
        
        let filename = UUID().uuidString + ".jpg"
        let storageRef = storage.child("images/\(filename)")
        
        storageRef.putData(imageData, metadata: nil) { metadata, error in
            guard let metadata = metadata else {
                completion(.failure(error ?? FirebaseError.unknownError))
                return
            }
            
            storageRef.downloadURL { url, error in
                guard let downloadURL = url else {
                    completion(.failure(error ?? FirebaseError.urlRetrievalFailed))
                    return
                }
                completion(.success(downloadURL.absoluteString))
            }
        }
    }
    
    // Upload multiple images and get an array of their URLs
    func uploadImages(images: [UIImage], completion: @escaping (Result<[String], Error>) -> Void) {
        var imageUrls = [String]()
        let dispatchGroup = DispatchGroup()
        
        for image in images {
            dispatchGroup.enter()
            uploadImage(image: image) { result in
                switch result {
                case .success(let url):
                    imageUrls.append(url)
                case .failure(let error):
                    dispatchGroup.leave()
                    completion(.failure(error))
                    return
                }
                dispatchGroup.leave()
            }
        }
        
        dispatchGroup.notify(queue: .main) {
            completion(.success(imageUrls))
        }
    }
    
    func uploadImageAndSaveContact(image: UIImage, contact: Contact, completion: @escaping (Error?) -> Void) {
        guard let imageData = image.jpegData(compressionQuality: 0.75) else {
            completion(FirebaseError.imageConversionFailed)
            return
        }
        
        let filename = UUID().uuidString + ".jpg"
        let storageRef = storage.child("images/\(filename)")
        
        storageRef.putData(imageData, metadata: nil) { metadata, error in
            guard metadata != nil else {
                completion(error ?? FirebaseError.unknownError)
                return
            }
            storageRef.downloadURL { url, error in
                guard let downloadURL = url else {
                    completion(error ?? FirebaseError.urlRetrievalFailed)
                    return
                }
                self.saveContact(contact: contact, photoURL: downloadURL.absoluteString, completion: completion)
            }
        }
    }
    
    private func saveContact(contact: Contact, photoURL: String, completion: @escaping (Error?) -> Void) {
        var contactData = contact.dictionary
        contactData["photoURL"] = photoURL  // Add the photo URL to the contact data
        
        db.collection("contacts").document(contact.id).setData(contactData) { error in
            completion(error)
        }
    }
    
    
    // Add a contact with image URLs to Firestore
    func addContact(contact: Contact, completion: @escaping (Error?) -> Void) {
        let contactData: [String: Any] = [
            "name": contact.name,
            "relation": contact.relation,
            "occupation": contact.occupation,
            "city": contact.city,
            "dateOfBirth": contact.dateOfBirth,
            "photoURLs": contact.photoURLs
        ]
        
        db.collection("contacts").document(contact.id).setData(contactData) { error in
            completion(error)
        }
    }
    
    // Fetch all contacts from Firestore
    func fetchContacts(completion: @escaping ([Contact], Error?) -> Void) {
        db.collection("contacts").getDocuments { snapshot, error in
            guard let documents = snapshot?.documents else {
                completion([], error)
                return
            }
            
            let contacts: [Contact] = documents.compactMap { doc -> Contact? in
                let data = doc.data()
                guard let name = data["name"] as? String,
                      let relation = data["relation"] as? String,
                      let occupation = data["occupation"] as? String,
                      let city = data["city"] as? String,
                      let dateOfBirth = data["dateOfBirth"] as? String,
                      let photoURLs = data["photoURLs"] as? [String] else {
                    return nil
                }
                
                return Contact(id: doc.documentID, name: name, relation: relation, occupation: occupation, city: city, dateOfBirth: dateOfBirth, photoURLs: photoURLs)
            }
            
            completion(contacts, nil)
        }
    }
    
    
    
    
    // Define the errors that could be encountered in the FirebaseService
    enum FirebaseError: Error {
        case imageConversionFailed
        case unknownError
        case urlRetrievalFailed
    }
}
