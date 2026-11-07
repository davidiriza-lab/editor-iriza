// Máscara de persona cuadro por cuadro con Vision (local). Escribe la máscara en gris crudo a stdout.
// Uso: swift estilo-cine/segmentar.swift video.mov ANCHO ALTO | ffmpeg -f rawvideo -pix_fmt gray -s ANCHOxALTO -i - mascaras/%05d.jpg
import Foundation
import AVFoundation
import Vision
import CoreImage

let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1]), ow = Int(a[2])!, oh = Int(a[3])!
let asset = AVURLAsset(url: url)
let track = asset.tracks(withMediaType: .video)[0]
let reader = try! AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
reader.add(out); reader.startReading()

let req = VNGeneratePersonSegmentationRequest()
req.qualityLevel = .accurate
req.outputPixelFormat = kCVPixelFormatType_OneComponent8
let ctx = CIContext(options: [.workingColorSpace: NSNull()])
var buf = [UInt8](repeating: 0, count: ow * oh)
var n = 0
let err = FileHandle.standardError
while let sb = out.copyNextSampleBuffer() {
  guard let px = CMSampleBufferGetImageBuffer(sb) else { continue }
  let h = VNImageRequestHandler(cvPixelBuffer: px, options: [:])
  try? h.perform([req])
  if let m = req.results?.first?.pixelBuffer {
    let ci = CIImage(cvPixelBuffer: m)
    let s = ci.transformed(by: CGAffineTransform(scaleX: CGFloat(ow) / ci.extent.width, y: CGFloat(oh) / ci.extent.height))
    ctx.render(s, toBitmap: &buf, rowBytes: ow, bounds: CGRect(x: 0, y: 0, width: ow, height: oh), format: .L8, colorSpace: nil)
  }
  buf.withUnsafeBufferPointer { FileHandle.standardOutput.write(Data(buffer: $0)) }
  n += 1
  if n % 100 == 0 { err.write("  máscara \(n)\n".data(using: .utf8)!) }
}
err.write("✓ \(n) máscaras\n".data(using: .utf8)!)
