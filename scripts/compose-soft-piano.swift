// Original soft piano composition. Render with macOS AVFoundation's piano bank.
import AVFoundation
import AudioToolbox
import Foundation

let engine = AVAudioEngine()
let piano = AVAudioUnitSampler()
let tone = AVAudioUnitEQ(numberOfBands: 1)
let room = AVAudioUnitReverb()
let format = AVAudioFormat(standardFormatWithSampleRate: 32000, channels: 2)!
engine.attach(piano)
engine.attach(tone)
engine.attach(room)
engine.connect(piano, to: tone, format: format)
engine.connect(tone, to: room, format: format)
engine.connect(room, to: engine.mainMixerNode, format: format)
tone.bands[0].filterType = .lowPass
tone.bands[0].frequency = 2800
tone.bands[0].bypass = false
room.loadFactoryPreset(.mediumHall)
room.wetDryMix = 13
let bank = URL(fileURLWithPath: "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls")
try piano.loadSoundBankInstrument(at: bank, program: 0, bankMSB: UInt8(kAUSampler_DefaultMelodicBankMSB), bankLSB: 0)

let beat = 60.0 / 64.0
let cycle = 64.0 * beat
struct Event {
    let frame: AVAudioFramePosition
    let note: UInt8
    let velocity: UInt8
    let channel: UInt8
    let on: Bool
}
var events: [Event] = []
func note(_ pitch: Int, _ start: Double, _ length: Double, _ velocity: Int, _ channel: Int) {
    events.append(Event(frame: Int64(start * 32000), note: UInt8(pitch), velocity: UInt8(velocity), channel: UInt8(channel), on: true))
    events.append(Event(frame: Int64((start + length) * 32000), note: UInt8(pitch), velocity: 0, channel: UInt8(channel), on: false))
}

// D6, G6 and Aadd9: consonant voicings, no bass drone or percussive chimes.
let chords = [[57,62,66,71], [55,59,62,64], [57,62,66,71], [57,61,64,71],
              [55,59,62,64], [57,62,66,71], [57,61,64,66], [57,62,66,69]]
let melody: [[(Double, Int, Double)]] = [
    [(1,62,1.8),(3,64,1.8),(5,66,2.6)],
    [(0,67,2.6),(3,66,1.8),(5,64,2.6)],
    [(1,62,1.8),(3,66,1.8),(5,69,2.6)],
    [(0,71,2.6),(3,69,1.8),(5,66,2.6)],
    [(0,67,2.6),(3,66,1.8),(5,64,2.6)],
    [(1,66,1.8),(3,64,1.8),(5,62,2.6)],
    [(1,64,1.8),(3,66,1.8),(5,69,2.6)],
    [(0,66,2.6),(3,64,1.8),(5,62,2.8)]
]
// Render two identical cycles; the second includes the first cycle's room tail.
for pass in 0..<2 {
    for bar in 0..<8 {
        let start = Double(pass) * cycle + Double(bar * 8) * beat
        for (i, pitch) in chords[bar].enumerated() {
            note(pitch, start + Double(i) * 0.24 * beat, 5.8 * beat, 23 + i % 2, 0)
        }
        for (i, item) in melody[bar].enumerated() {
            note(item.1, start + item.0 * beat, item.2 * beat, 37 + (i == 1 ? 2 : 0), 1)
        }
    }
}
events.sort { $0.frame == $1.frame ? (!$0.on && $1.on) : $0.frame < $1.frame }
try engine.enableManualRenderingMode(.offline, format: format, maximumFrameCount: 1024)
try engine.start()
let output = URL(fileURLWithPath: CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "output/soft-piano-render.wav")
try FileManager.default.createDirectory(at: output.deletingLastPathComponent(), withIntermediateDirectories: true)
var file: AVAudioFile? = try AVAudioFile(forWriting: output, settings: format.settings)
let buffer = AVAudioPCMBuffer(pcmFormat: engine.manualRenderingFormat, frameCapacity: 1024)!
var index = 0
let end = Int64(cycle * 2 * 32000)
while engine.manualRenderingSampleTime < end {
    let current = engine.manualRenderingSampleTime
    while index < events.count && events[index].frame <= current {
        let event = events[index]
        if event.on { piano.startNote(event.note, withVelocity: event.velocity, onChannel: event.channel) }
        else { piano.stopNote(event.note, onChannel: event.channel) }
        index += 1
    }
    let next = index < events.count ? events[index].frame : end
    let count = AVAudioFrameCount(min(1024, end - current, max(1, next - current)))
    let status = try engine.renderOffline(count, to: buffer)
    if status == .success { try file!.write(from: buffer) }
    else if status == .error { fatalError("Offline rendering failed") }
}
engine.stop()
file = nil
print("Rendered original 60-second soft piano loop with harmonic accompaniment: \(output.path)")
