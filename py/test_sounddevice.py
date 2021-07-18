from numpy import ndarray
import sounddevice as sd
from scipy.io.wavfile import write

def save(indata, outdata, frames, time, status):
    print(indata)

print(sd.query_devices())

fs = 44100  # Sample rate
seconds = 3  # Duration of recording

sd.InputStream(samplerate = 44100.0, device=6, channels=1, callback=save, dtype = 'int16')

while(True):
    print(".")
    # x=1

# myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
# sd.wait()  # Wait until recording is finished
# write('output.wav', fs, myrecording)  # Save as WAV file

print("foo") 