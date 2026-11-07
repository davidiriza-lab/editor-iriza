// Lee TODOS los fotogramas del video FINAL con Vision: caras y texto en pantalla (OCR), para la revisión final.
// Uso: bin/fotogramas video.mp4 salida.json [cada_n]        (compilar: swiftc -O fotogramas.swift -o bin/fotogramas)
//   cada_n = 1 (todos los fotogramas, por defecto) · 2 = uno sí y uno no, etc.
// Salida: {"w","h","fps","f":[{"i":n,"t":s,"caras":[[x0,y0,x1,y1],…],"texto":[["palabra",x0,y0,x1,y1],…] (una caja por palabra)}]}  (px, y hacia abajo)
import Foundation
import AVFoundation
import Vision

let a = CommandLine.arguments
guard a.count >= 3 else { print("uso: fotogramas video salida.json [cada_n]"); exit(1) }
let cada = a.count >= 4 ? max(1, Int(a[3]) ?? 1) : 1
let asset = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let vt = asset.tracks(withMediaType: .video)[0]
let tam = vt.naturalSize.applying(vt.preferredTransform)
let W = Double(abs(tam.width)), H = Double(abs(tam.height)), fps = Double(vt.nominalFrameRate)
let reader = try! AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: vt, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
out.alwaysCopiesSampleData = false; reader.add(out); reader.startReading()

let caras = VNDetectFaceRectanglesRequest()
let texto = VNRecognizeTextRequest(); texto.recognitionLevel = .accurate; texto.usesLanguageCorrection = false
texto.recognitionLanguages = ["es-ES", "en-US"]; texto.minimumTextHeight = 0.012
func caja(_ b: CGRect) -> [Double] {
  [(b.minX * W).rounded(), ((1 - b.maxY) * H).rounded(), (b.maxX * W).rounded(), ((1 - b.minY) * H).rounded()]
}
var filas: [[String: Any]] = []; var i = -1
while let s = out.copyNextSampleBuffer() {
  i += 1; if i % cada != 0 { continue }
  guard let px = CMSampleBufferGetImageBuffer(s) else { continue }
  let t = CMSampleBufferGetPresentationTimeStamp(s).seconds
  try? VNImageRequestHandler(cvPixelBuffer: px, options: [:]).perform([caras, texto])
  let cs = (caras.results ?? []).map { caja($0.boundingBox) }
  // una caja por PALABRA (Vision junta en un renglón texto del fondo con el subtítulo; por palabra se separan)
  var ts: [[Any]] = []
  for o in texto.results ?? [] {
    guard let c = o.topCandidates(1).first else { continue }
    let str = c.string
    str.enumerateSubstrings(in: str.startIndex..<str.endIndex, options: .byWords) { w, r, _, _ in
      guard let w = w, let bb = try? c.boundingBox(for: r)?.boundingBox else { return }
      ts.append([w] + caja(bb).map { $0 as Any })
    }
  }
  filas.append(["i": i, "t": (t * 1000).rounded() / 1000, "caras": cs, "texto": ts])
}
let json: [String: Any] = ["w": W, "h": H, "fps": fps, "f": filas]
try! JSONSerialization.data(withJSONObject: json).write(to: URL(fileURLWithPath: a[2]))
print("✓ \(filas.count) fotogramas leídos (cara + texto) · \(a[2])")
