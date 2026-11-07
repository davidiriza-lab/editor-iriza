// Quita el fondo de una imagen con Vision (el mismo "Copiar sujeto" de macOS). Local y gratis.
// Uso: swift estilo-cine/recortar.swift entrada.png salida.png
import Foundation
import Vision
import CoreImage
import CoreImage.CIFilterBuiltins
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count >= 3 else { print("Uso: recortar.swift entrada salida.png"); exit(1) }
let entrada = URL(fileURLWithPath: args[1]), salida = URL(fileURLWithPath: args[2])
guard let img = CIImage(contentsOf: entrada) else { print("No pude abrir \(args[1])"); exit(1) }

let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: img)
do { try handler.perform([req]) } catch { print("Vision falló: \(error)"); exit(1) }
guard let res = req.results?.first, !res.allInstances.isEmpty else { print("✗ no encontré un sujeto en \(args[1])"); exit(2) }

let buf = try res.generateMaskedImage(ofInstances: res.allInstances, from: handler, croppedToInstancesExtent: false)
let recorte = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
guard let cg = ctx.createCGImage(recorte, from: recorte.extent),
      let dest = CGImageDestinationCreateWithURL(salida as CFURL, UTType.png.identifier as CFString, 1, nil) else { exit(1) }
CGImageDestinationAddImage(dest, cg, nil)
CGImageDestinationFinalize(dest)
print("✓ \(args[2])  (\(res.allInstances.count) sujeto(s))")
