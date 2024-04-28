import Foundation
import FirebaseFirestore
import FirebaseFirestoreSwift

struct Contact: Identifiable, Codable {
        var id: String
        var name: String
        var relation: String
        var occupation: String
        var city: String
        var dateOfBirth: String  // Assuming dateOfBirth is a string in Firestore
        var photoURLs: [String]  // Assuming this is an array of strings in Firestore

    
    enum CodingKeys: String, CodingKey {
            case id
            case name
            case relation
            case occupation
            case city
            case dateOfBirth
            case photoURLs
        }


    var dictionary: [String: Any] {
        return [
            "name": name,
            "relation": relation,
            "occupation": occupation,
            "city": city,
            "dateOfBirth": dateOfBirth // Save as timestamp
        ]
    }
}
