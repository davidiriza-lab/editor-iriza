// Convierte video HDR (HLG / PQ, BT.2020, p. ej. DJI en modo HLG) a SDR Rec.709 con el mapeo de tonos de macOS.
// Uso: bin/sdr entrada.mp4 salida.mov [ancho alto]      (compilar: swiftc -O estilo-cine/sdr.swift -o bin/sdr)
// Sale H.264 8 bits Rec.709 (calidad alta) con el audio copiado. Si el video ya es Rec.709 no hace falta usarlo.
import Foundation
import AVFoundation
import VideoToolbox

let a = CommandLine.arguments
guard a.count >= 3 else { print("uso: sdr entrada salida [ancho alto]"); exit(1) }
let src = URL(fileURLWithPath: a[1]), dst = URL(fileURLWithPath: a[2])
try? FileManager.default.removeItem(at: dst)
let asset = AVURLAsset(url: src)
let vt = asset.tracks(withMediaType: .video)[0]
let tam = vt.naturalSize.applying(vt.preferredTransform)
let W = a.count >= 5 ? Int(a[3])! : Int(abs(tam.width)), H = a.count >= 5 ? Int(a[4])! : Int(abs(tam.height))

let color: [String: Any] = [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                            AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                            AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2]
// composición: aplica rotación y fuerza el espacio de color 709 → AVFoundation hace el tone mapping HDR→SDR
let comp = AVMutableVideoComposition(propertiesOf: asset)
comp.colorPrimaries = AVVideoColorPrimaries_ITU_R_709_2
comp.colorTransferFunction = AVVideoTransferFunction_ITU_R_709_2
comp.colorYCbCrMatrix = AVVideoYCbCrMatrix_ITU_R_709_2
comp.renderSize = CGSize(width: W, height: H)
let ins = AVMutableVideoCompositionInstruction(); ins.timeRange = CMTimeRange(start: .zero, duration: asset.duration)
let li = AVMutableVideoCompositionLayerInstruction(assetTrack: vt)
let sx = CGFloat(W) / abs(tam.width), sy = CGFloat(H) / abs(tam.height)
li.setTransform(vt.preferredTransform.concatenating(CGAffineTransform(scaleX: sx, y: sy)), at: .zero)
ins.layerInstructions = [li]; comp.instructions = [ins]

let reader = try! AVAssetReader(asset: asset)
let vout = AVAssetReaderVideoCompositionOutput(videoTracks: [vt], videoSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
vout.videoComposition = comp; reader.add(vout)
let at = asset.tracks(withMediaType: .audio).first
var aout: AVAssetReaderTrackOutput? = nil
if let at = at { aout = AVAssetReaderTrackOutput(track: at, outputSettings: [AVFormatIDKey: kAudioFormatLinearPCM]); reader.add(aout!) }

let writer = try! AVAssetWriter(outputURL: dst, fileType: .mov)
let vin = AVAssetWriterInput(mediaType: .video, outputSettings: [
  AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H, AVVideoColorPropertiesKey: color,
  AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: W * H * 30 / 4, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
vin.expectsMediaDataInRealTime = false; writer.add(vin)
var ain: AVAssetWriterInput? = nil
// el audio va como PCM sin comprimir para no perder calidad
if aout != nil { ain = AVAssetWriterInput(mediaType: .audio, outputSettings: [AVFormatIDKey: kAudioFormatLinearPCM, AVLinearPCMBitDepthKey: 16, AVLinearPCMIsFloatKey: false, AVLinearPCMIsBigEndianKey: false, AVLinearPCMIsNonInterleaved: false, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 2]); writer.add(ain!) }
reader.startReading(); writer.startWriting(); writer.startSession(atSourceTime: .zero)
let g = DispatchGroup(), q1 = DispatchQueue(label: "v"), q2 = DispatchQueue(label: "a")
g.enter()
vin.requestMediaDataWhenReady(on: q1) {
  while vin.isReadyForMoreMediaData {
    if let s = vout.copyNextSampleBuffer() { vin.append(s) } else { vin.markAsFinished(); g.leave(); return }
  }
}
if let ain = ain, let aout = aout {
  g.enter()
  ain.requestMediaDataWhenReady(on: q2) {
    while ain.isReadyForMoreMediaData {
      if let s = aout.copyNextSampleBuffer() { ain.append(s) } else { ain.markAsFinished(); g.leave(); return }
    }
  }
}
g.wait()
let sem = DispatchSemaphore(value: 0); writer.finishWriting { sem.signal() }; sem.wait()
if writer.status != .completed { print("✗", writer.error ?? "error"); exit(1) }
print("✓ \(dst.lastPathComponent) \(W)x\(H) Rec.709")
