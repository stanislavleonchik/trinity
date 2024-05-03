//
//  ContentView.swift
//  trinity-app
//
//  Created by Stanislav Leonchik on 16.02.2024.
//

import SwiftUI
import UniformTypeIdentifiers


struct Collocation: Identifiable, Codable {
    var id: UUID = UUID()
    var coloc: String
    var count: Int
    var translation: String
    enum CodingKeys: String, CodingKey {
            case coloc, count, translation
        }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        coloc = try container.decode(String.self, forKey: .coloc)
        count = try container.decode(Int.self, forKey: .count)
        translation = try container.decode(String.self, forKey: .translation)
        id = UUID()
    }
}

struct GrammarExercise: Identifiable, Codable {
    var id = UUID()
    var rawVerb: String
    var readyVerb: String
    var sentence: String
    
    enum CodingKeys: String, CodingKey {
            case rawVerb = "raw_verb"
            case readyVerb = "ready_verb"
            case sentence
        }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        rawVerb = try container.decode(String.self, forKey: .rawVerb)
        readyVerb = try container.decode(String.self, forKey: .readyVerb)
        sentence = try container.decode(String.self, forKey: .sentence)
        id = UUID()
    }
}

struct ContentView: View {
    @State private var serverResponse = ""
    @State private var isImporting = false
    @State private var documentData: Data?
    @State private var fileName: String?
    @State private var collocations: [Collocation] = []

    
    var body: some View {
        TabView {
            VStack {
                Button("Загрузить PDF") {
                                isImporting = true
                            }
                            .fileImporter(
                                isPresented: $isImporting,
                                allowedContentTypes: [UTType.pdf],
                                allowsMultipleSelection: false
                            ) { result in
                                switch result {
                                case .success(let urls):
                                    guard let url = urls.first, url.startAccessingSecurityScopedResource() else { return }
                                    self.fileName = url.lastPathComponent

                                    defer { url.stopAccessingSecurityScopedResource() }
                                    if let data = try? Data(contentsOf: url) {
                                        documentData = data
                                        uploadPDF(data: data)
                                    }
                                case .failure(let error):
                                    print("Не удалось загрузить файл: \(error.localizedDescription)")
                                }
                            }
                            
                            if let data = documentData {
                                Text("Файл \(fileName ?? "-")")
                            }
                List(collocations, id: \.id) { collocation in
                    VStack(alignment: .leading) {
                        Text(collocation.coloc).font(.headline)
                        Text("Количество упоминаний: \(collocation.count)").font(.subheadline)
                        Text("Перевод: \(collocation.translation)").font(.subheadline).foregroundColor(.gray)
                    }
                }
                        .onAppear(perform: loadCollocations)
            }
                .tabItem {
                    Image(systemName: "text.word.spacing")
                    Text("Collocations")
                }
            
            // Вторая вкладка
            TensesView()
            .tabItem {
                Label("Tenses", systemImage: "text.redaction")
            }
        }
    }
    
    func uploadPDF(data: Data) {
        let url = URL(string: "http://127.0.0.1:5000/upload-pdf")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"filename.pdf\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/pdf\r\n\r\n".data(using: .utf8)!)
        body.append(data)
        body.append("\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Ошибка при отправке файла: \(error.localizedDescription)")
                return
            }
            if let response = response as? HTTPURLResponse {
                print("Статус код ответа: \(response.statusCode)")
            }
        }.resume()
    }
    
    func loadCollocations() {
        guard let url = URL(string: "http://127.0.0.1:5000/collocations") else {
            print("Invalid URL")
            return
        }

        URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                do {
                    let decodedResponse = try JSONDecoder().decode([Collocation].self, from: data)
                    DispatchQueue.main.async {
                        self.collocations = decodedResponse
                    }
                } catch {
                    print("Decoding failed: \(error)")
                }
            } else if let error = error {
                print("HTTP Request Failed \(error)")
            }
        }.resume()
    }


}

struct TensesView: View {
    @State private var exercises: [GrammarExercise] = []
    @State private var answers: [UUID: String] = [:]
    @State private var feedback: [UUID: String] = [:]

    var body: some View {
        List(exercises, id: \.id) { exercise in
            VStack(alignment: .leading) {
                Text(exercise.sentence.replacingOccurrences(of: "______", with: String(repeating: "_", count: exercise.readyVerb.count)))
                    .padding()
                Text("Исходная форма глагола: \(exercise.rawVerb)")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                TextField("Enter the correct form of the verb", text: Binding<String>(
                    get: { self.answers[exercise.id] ?? "" },
                    set: { self.answers[exercise.id] = $0 }
                ))
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
                Button("Check") {
                    if answers[exercise.id, default: ""].lowercased() == exercise.readyVerb.lowercased() {
                        feedback[exercise.id] = "Correct!"
                    } else {
                        feedback[exercise.id] = "Incorrect, try again!"
                    }
                }
                if let result = feedback[exercise.id] {
                    Text(result)
                        .foregroundColor(result == "Correct!" ? .green : .red)
                }
            }
        }
        .onAppear(perform: loadExercises)
    }

    func loadExercises() {
            guard let url = URL(string: "http://127.0.0.1:5000/tense") else {
                print("Invalid URL")
                return
            }

            URLSession.shared.dataTask(with: url) { data, response, error in
                if let data = data {
                    do {
                        let decodedResponse = try JSONDecoder().decode([GrammarExercise].self, from: data)
                        DispatchQueue.main.async {
                            self.exercises = decodedResponse
                        }
                    } catch {
                        print("Decoding failed: \(error)")
                    }
                } else if let error = error {
                    print("HTTP Request Failed \(error)")
                }
            }.resume()
        }
}


#Preview {
    ContentView()
}



