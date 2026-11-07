// Tope de la cabeza (silueta) y manos (≈ celular) cada N segundos, con Vision.
// Uso: swift estilo-cine/manos.swift video.mov desde hasta paso  → una línea por muestra: t cabeza_y manos_min_y manos_max_y
// (fracciones del alto, 0 = arriba; -1 si no hay manos)
import Foundation
import AVFoundation
import Vision

let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1]); let desde = Double(a[2])!, hasta = Double(a[3])!, paso = Double(a[4])!
let asset = AVURLAsset(url: url)
let gen = AVAssetImageGenerator(asset: asset); gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = .zero; gen.requestedTimeToleranceAfter = .zero
gen.maximumSize = CGSize(width: 720, height: 1280)
let manos = VNDetectHumanHandPoseRequest(); manos.maximumHandCount = 2
let persona = VNGeneratePersonSegmentationRequest(); persona.qualityLevel = .balanced
persona.outputPixelFormat = kCVPixelFormatType_OneComponent8
var t = desde
while t <= hasta {
  if let img = try? gen.copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil) {
    let h = VNImageRequestHandler(cgImage: img, options: [:])
    try? h.perform([manos, persona])
    var lo = 2.0, hi = -1.0
    for obs in manos.results ?? [] {
      if let pts = try? obs.recognizedPoints(.all) {
        for (_, p) in pts where p.confidence > 0.3 { let y = 1 - Double(p.location.y); lo = min(lo, y); hi = max(hi, y) }
      }
    }
    var cabeza = -1.0
    if let m = persona.results?.first?.pixelBuffer {
      CVPixelBufferLockBaseAddress(m, .readOnly)
      let w = CVPixelBufferGetWidth(m), hh = CVPixelBufferGetHeight(m), row = CVPixelBufferGetBytesPerRow(m)
      let base = CVPixelBufferGetBaseAddress(m)!.assumingMemoryBound(to: UInt8.self)
      outer: for y in 0..<hh { var c = 0; for x in 0..<w { if base[y * row + x] > 128 { c += 1 } }; if c > w / 30 { cabeza = Double(y) / Double(hh); break outer } }
      CVPixelBufferUnlockBaseAddress(m, .readOnly)
    }
    print(String(format: "%.2f %.3f %.3f %.3f", t, cabeza, hi < 0 ? -1 : lo, hi))
  }
  t += paso
}
