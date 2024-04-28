import SwiftUI

struct ContentView: View {
    @State private var image: UIImage?
    @State private var isCameraPresented = false

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                if let image = image {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                }
                Button("Open Camera") {
                    isCameraPresented = true
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)

                NavigationLink("Add Contact", destination: AddContactView())
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)

                NavigationLink("View Contacts", destination: ContactsListView())
                    .padding()
                    .background(Color.orange)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .sheet(isPresented: $isCameraPresented) {
                CameraView(image: $image)
            }
            .navigationTitle("Home")
        }
    }
}
