import Foundation
import UIKit

class ViewController: UIViewController, UIImagePickerControllerDelegate, UINavigationControllerDelegate {

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCameraButton()
    }

    func setupCameraButton() {
        let cameraButton = UIButton(frame: CGRect(x: (view.frame.width - 200) / 2, y: view.frame.height - 100, width: 200, height: 50))
        cameraButton.backgroundColor = .systemBlue
        cameraButton.setTitle("Open Camera", for: .normal)
        cameraButton.addTarget(self, action: #selector(openCameraAction), for: .touchUpInside)
        self.view.addSubview(cameraButton)
    }

    @objc func openCameraAction() {
        openCamera()
    }

    func openCamera() {
        guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
            print("Camera not available")
            return
        }

        let imagePickerController = UIImagePickerController()
        imagePickerController.delegate = self
        imagePickerController.sourceType = .camera
        imagePickerController.allowsEditing = false  // Set to true if editing is needed
        present(imagePickerController, animated: true, completion: nil)
    }

    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
        picker.dismiss(animated: true, completion: nil)
        guard let image = info[.originalImage] as? UIImage else {
            print("No image found")
            return
        }
        
        sendImageToServer(image: image)
    }

    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true, completion: nil)
    }

    func sendImageToServer(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.9) else {
            print("Could not get JPEG representation of UIImage")
            return
        }

        let url = URL(string: "http://192.168.x.x:5000/recognize")!  // Replace with your Flask server's IP and endpoint
        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        request.httpBody = body

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, error == nil else {
                print("Error:", error?.localizedDescription ?? "Unknown error")
                return
            }

            if let jsonResponse = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
               let contactURL = jsonResponse["contactURL"] as? String {
                print("Contact URL:", contactURL)
            }
        }
        task.resume()
    }
}
