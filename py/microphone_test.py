import pyaudio
import wave

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(i, p.get_device_info_by_index(i)["name"])
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 4096
RECORD_SECONDS = 5
INPUT_DEVICE = 11
 
audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK,
                input_device_index=INPUT_DEVICE
                )
print("recording...")
frames = []
 
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("finished recording")
 
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
 
waveFile = wave.open(f"file{INPUT_DEVICE}.wav", 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()