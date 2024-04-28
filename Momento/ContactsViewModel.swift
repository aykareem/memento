import FirebaseFirestore
import Combine

class ContactsViewModel: ObservableObject {
    @Published var contacts = [Contact]()
    private var db = Firestore.firestore()

    init() {
        fetchContacts()
    }

    func fetchContacts() {
        db.collection("contacts").order(by: "name").addSnapshotListener { [weak self] (querySnapshot, error) in
            if let error = error {
                print("Error fetching contacts: \(error)")
            } else {
                // Perform the update in the main thread if dealing with UI updates
                DispatchQueue.main.async {
                    self?.contacts = querySnapshot?.documents.compactMap { document in
                        // Here we're manually creating a Contact instance from the document.
                        return Contact(id: document.documentID,
                                       name: document["name"] as? String ?? "",
                                       relation: document["relation"] as? String ?? "",
                                       occupation: document["occupation"] as? String ?? "",
                                       city: document["city"] as? String ?? "",
                                       dateOfBirth: document["dateOfBirth"] as? String ?? "",
                                       photoURLs: document["photoURLs"] as? [String] ?? [])
                    } ?? []
                }
            }
        }
    }
}
