import SwiftUI

struct ContentView: View {
    @State private var image: UIImage?
    @State private var isCameraPresented = false

    var body: some View {
        VStack {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
            }
            Button("Open Camera") {
                isCameraPresented = true
            }
        }
        .sheet(isPresented: $isCameraPresented) {
            CameraView(image: $image)
        }
    }
}


