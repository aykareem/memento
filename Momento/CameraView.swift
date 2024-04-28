import SwiftUI
import UIKit
import FirebaseStorage
import FirebaseFirestore

struct CameraView: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.presentationMode) var presentationMode

    func makeUIViewController(context: UIViewControllerRepresentableContext<Self>) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .camera
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: UIViewControllerRepresentableContext<Self>) {
        // No update code needed for the basic functionality
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        var parent: CameraView

        init(_ parent: CameraView) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let uiImage = info[.originalImage] as? UIImage {
                parent.image = uiImage
                parent.uploadImageToFirebase(image: uiImage)
            }
            parent.presentationMode.wrappedValue.dismiss()
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
    }

    private func uploadImageToFirebase(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.75) else { return }

        let storageRef = Storage.storage().reference().child("images/\(UUID().uuidString).jpg")
        storageRef.putData(imageData, metadata: nil) { metadata, error in
            guard let _ = metadata else {
                print("Error uploading image: \(error?.localizedDescription ?? "Unknown error")")
                return
            }

            storageRef.downloadURL { url, error in
                guard let downloadURL = url else {
                    print("Error getting download URL: \(error?.localizedDescription ?? "Unknown error")")
                    return
                }

                self.saveImageURLToFirestore(imageURL: downloadURL.absoluteString)
            }
        }
    }

    private func saveImageURLToFirestore(imageURL: String) {
        let db = Firestore.firestore()
        let data = ["imageURL": imageURL, "timestamp": FieldValue.serverTimestamp()] as [String: Any]
        db.collection("images").addDocument(data: data) { error in
            if let error = error {
                print("Error saving image to Firestore: \(error.localizedDescription)")
            } else {
                print("Successfully saved image URL to Firestore.")
            }
        }
    }
}

