import SwiftUI

struct AddContactView: View {
    @State private var name: String = ""
    @State private var relation: String = ""
    @State private var occupation: String = ""
    @State private var city: String = ""
    @State private var dateOfBirth: String = ""
    @State private var showingImagePicker = false
    @State private var images: [UIImage] = []
    @State private var isUploading = false
    
    private let firebaseService = FirebaseService()

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Contact Details")) {
                    TextField("Name", text: $name)
                    TextField("Relation", text: $relation)
                    TextField("Occupation", text: $occupation)
                    TextField("City", text: $city)
                    TextField("Date of Birth", text: $dateOfBirth )
                }

                Section(header: Text("Images")) {
                    ForEach(images, id: \.self) { image in
                        Image(uiImage: image)
                            .resizable()
                            .scaledToFit()
                            .frame(height: 100)
                    }

                    Button(action: {
                        self.showingImagePicker = true
                    }) {
                        Text("Add Image")
                    }
                }
                
                if isUploading {
                    Section {
                        HStack {
                            Spacer()
                            ProgressView("Uploading...")
                            Spacer()
                        }
                    }
                }
            }
            .navigationBarTitle("Add New Contact")
            .navigationBarItems(trailing: Button("Save") {
                self.saveContact()
            })
            .sheet(isPresented: $showingImagePicker) {
                ImagePicker(images: $images)
            }
        }
    }

    func saveContact() {
        isUploading = true
        firebaseService.createContactWithImages(name: name, relation: relation, occupation: occupation, city: city, dateOfBirth: dateOfBirth, images: images) { error in
            isUploading = false
            if let error = error {
                print("Error: \(error.localizedDescription)")
                // Handle the error appropriately, perhaps show an alert
            } else {
                print("Contact successfully created with images.")
                // Handle success, maybe clear the form or show a success message
                clearForm()
            }
        }
    }

    func clearForm() {
        name = ""
        relation = ""
        occupation = ""
        city = ""
        dateOfBirth = ""
        images.removeAll()
    }
}

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var images: [UIImage]
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIViewController(context: Context) -> some UIViewController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIViewControllerType, context: Context) {}

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.images.append(image)
            }

            picker.dismiss(animated: true)
        }
    }
}
