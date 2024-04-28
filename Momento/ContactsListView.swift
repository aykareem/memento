import SwiftUI

struct ContactsListView: View {
    @ObservedObject var viewModel = ContactsViewModel()

    var body: some View {
        List(viewModel.contacts) { contact in
            VStack(alignment: .leading) {
                // Style the text to differentiate between labels and data
                Group {
                    HStack {
                        Text("Name:").fontWeight(.bold)
                        Spacer()
                        Text(contact.name)
                    }
                    HStack {
                        Text("Relation:").fontWeight(.bold)
                        Spacer()
                        Text(contact.relation)
                    }
                    HStack {
                        Text("Occupation:").fontWeight(.bold)
                        Spacer()
                        Text(contact.occupation)
                    }
                    HStack {
                        Text("City:").fontWeight(.bold)
                        Spacer()
                        Text(contact.city)
                    }
                    HStack {
                        Text("Date of Birth:").fontWeight(.bold)
                        Spacer()
                        Text(contact.dateOfBirth)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                
                if !contact.photoURLs.isEmpty {
                                    Text("Photos:").fontWeight(.bold)
                                    ForEach(contact.photoURLs, id: \.self) { photoURL in
                                        if let url = URL(string: photoURL) {
                                            // AsyncImage to load images from the web
                                            AsyncImage(url: url) { image in
                                                image
                                                    .resizable()
                                                    .scaledToFit()
                                                    .frame(height: 500) // Set the frame as needed
                                            } placeholder: {
                                                ProgressView() // Show a loader while the image is loading
                                            }
                                        } else {
                                            Text("Invalid URL")
                                        }
                                    }
                                }
                            }
                        }
                        .onAppear {
                            viewModel.fetchContacts()
                        }
                    }
                }
