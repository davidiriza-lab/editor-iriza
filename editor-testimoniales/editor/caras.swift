// Detecta la cara (y la silueta de la persona) en TODOS los fotogramas de un video, con Vision.
// Uso: bin/caras video.mp4 salida.json [desde hasta paso]   (compilar: swiftc -O caras.swift -o bin/caras)
//   sin desde/hasta: todos los fotogramas · con ellos: solo ese tramo, un fotograma cada `paso` s (para encuadrar)
// Salida: {"w":1080,"h":1920,"fps":29.97,"f":[[t, x0,y0,x1,y1, cabeza_y], ...]} en px del video, y hacia abajo.
//   x0..y1 = caja de la cara más grande (-1 si no hay cara) · cabeza_y = punto más alto de la silueta (-1 si no hay persona)
import Foundation
import AVFoundation
import Vision

let a = CommandLine.arguments
guard a.count >= 3 else { print("uso: caras video salida.json"); exit(1) }
let asset = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let vt = asset.tracks(withMediaType: .video)[0]
let tam = vt.naturalSize.applying(vt.preferredTransform)
let W = abs(tam.width), H = abs(tam.height), fps = Double(vt.nominalFrameRate)
let reader = try! AVAssetReader(asset: asset)
var paso = 0.0
if a.count >= 6, let d = Double(a[3]), let h = Double(a[4]), let p = Double(a[5]) {
  reader.timeRange = CMTimeRange(start: CMTime(seconds: d, preferredTimescale: 600), end: CMTime(seconds: h, preferredTimescale: 600)); paso = p }
var siguiente = -1.0
let out = AVAssetReaderTrackOutput(track: vt, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
out.alwaysCopiesSampleData = false; reader.add(out); reader.startReading()

let caras = VNDetectFaceRectanglesRequest()
let persona = VNGeneratePersonSegmentationRequest(); persona.qualityLevel = .fast
persona.outputPixelFormat = kCVPixelFormatType_OneComponent8
var filas: [[Double]] = []
while let s = out.copyNextSampleBuffer() {
  guard let px = CMSampleBufferGetImageBuffer(s) else { continue }
  let t = CMSampleBufferGetPresentationTimeStamp(s).seconds
  if paso > 0 { if t < siguiente { continue }; siguiente = t + paso }
  let h = VNImageRequestHandler(cvPixelBuffer: px, options: [:])
  try? h.perform([caras, persona])
  var f: [Double] = [t, -1, -1, -1, -1, -1]
  if let c = (caras.results ?? []).max(by: { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height }) {
    let b = c.boundingBox   // Vision: origen abajo-izquierda, proporciones
    f[1] = Double(b.minX * W); f[3] = Double(b.maxX * W)
    f[2] = Double((1 - b.maxY) * H); f[4] = Double((1 - b.minY) * H)
  }
  if let m = persona.results?.first?.pixelBuffer {
    CVPixelBufferLockBaseAddress(m, .readOnly)
    let mw = CVPixelBufferGetWidth(m), mh = CVPixelBufferGetHeight(m), st = CVPixelBufferGetBytesPerRow(m)
    let p = CVPixelBufferGetBaseAddress(m)!.assumingMemoryBound(to: UInt8.self)
    var top = -1
    fila: for y in 0..<mh { var n = 0; for x in stride(from: 0, to: mw, by: 2) where p[y * st + x] > 128 { n += 1; if n > mw / 60 { top = y; break fila } } }
    CVPixelBufferUnlockBaseAddress(m, .readOnly)
    if top >= 0 { f[5] = Double(top) / Double(mh) * Double(H) }
  }
  filas.append(f.map { ($0 * 10).rounded() / 10 })
}
let json: [String: Any] = ["w": Double(W), "h": Double(H), "fps": fps, "f": filas]
try! JSONSerialization.data(withJSONObject: json).write(to: URL(fileURLWithPath: a[2]))
let conCara = filas.filter { $0[1] >= 0 }.count
print("✓ \(filas.count) fotogramas · cara en \(conCara) · \(a[2])")
