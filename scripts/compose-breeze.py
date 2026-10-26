"""Original airy ambience: a soft breeze and sparse major-pentatonic chimes."""
from pathlib import Path
import wave
import numpy as np

RATE = 32000
DURATION = 60
COUNT = RATE * DURATION
rng = np.random.default_rng(33)
t = np.arange(COUNT) / RATE
frequencies = np.fft.rfftfreq(COUNT, 1 / RATE)
mix = np.zeros((COUNT, 2))


def wind_texture():
    # Filtering in the frequency domain gives a periodic, seamless noise bed.
    spectrum = np.fft.rfft(rng.normal(size=COUNT))
    f = np.maximum(frequencies, 1)
    pink = 1 / np.sqrt(f)
    high_pass = 1 - np.exp(-(f / 180) ** 4)
    low_pass = np.exp(-(f / 1500) ** 2)
    sound = np.fft.irfft(spectrum * pink * high_pass * low_pass, n=COUNT)
    return sound / np.std(sound)


common = wind_texture()
# Three slow, periodic swells: air moving gently, without loud gusts or rumble.
breath = .65 + .14 * np.sin(2 * np.pi * t / 20)
breath += .09 * np.sin(2 * np.pi * t / 12 + .7)
breath += .04 * np.cos(2 * np.pi * t / 7.5)
for channel in range(2):
    side = wind_texture()
    mix[:, channel] = (.88 * common + .12 * side) * breath * .025


def add_wrap(sound, start, pan=0, gain=1):
    start = round(start * RATE) % COUNT
    stereo = sound[:, None] * np.array([
        np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    ]) * gain
    first = min(len(stereo), COUNT - start)
    mix[start:start + first] += stereo[:first]
    if first < len(stereo):
        mix[:len(stereo) - first] += stereo[first:]


def chime(midi):
    f = 440 * 2 ** ((midi - 69) / 12)
    local = np.arange(RATE * 7) / RATE
    sound = np.zeros_like(local)
    # A rounded, bamboo-like chime rather than a sharp metallic bell.
    for ratio, amplitude, decay in [(1, .85, 2.2), (2.002, .12, 1.3), (3, .025, .65)]:
        sound += amplitude * np.sin(2 * np.pi * f * ratio * local) * np.exp(-local / decay)
    sound *= (1 - np.exp(-local / .055)) * np.minimum(1, (7 - local) / .3)
    return sound


# D-major pentatonic: open, gently ascending fragments with generous silence.
notes = [(2.4, 74), (6.1, 76), (10.8, 78), (17.3, 81),
         (22.6, 78), (29.4, 76), (35.2, 74), (40.7, 78),
         (44.9, 81), (50.3, 83), (55.1, 81)]
for i, (start, midi) in enumerate(notes):
    note = chime(midi)
    pan = [-.32, .24, -.08, .35][i % 4]
    strength = [.065, .052, .058][i % 3]
    add_wrap(note, start, pan, strength)
    for delay, gain in [(.19, .12), (.43, .075), (.79, .04), (1.31, .022)]:
        add_wrap(note, start + delay, -pan, strength * gain)

mix -= mix.mean(axis=0)
# Quiet, audible ambience with generous peak headroom.
rms = np.sqrt(np.mean(mix ** 2))
mix *= .065 / rms
peak = np.max(np.abs(mix))
if peak > .38:
    mix *= .38 / peak
output = Path(__file__).resolve().parents[1] / 'output' / 'music-breeze.wav'
output.parent.mkdir(exist_ok=True)
with wave.open(str(output), 'wb') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(RATE)
    wav.writeframes((mix * 32767).astype('<i2').tobytes())
print(f'Original breeze ambience: {DURATION}s, stereo, seamless loop. {output}')
