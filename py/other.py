import pyaudio

FRAMES_PERBUFF = 256 # number of frames per buffer
FORMAT = pyaudio.paInt16 # 16 bit int
CHANNELS = 1 # I guess this is for mono sounds
FRAME_RATE = 44100 # sample rate
device_id = 6

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                input_device_index=device_id,
                
                rate=FRAME_RATE,
                input=True,
                frames_per_buffer=FRAMES_PERBUFF) #buffer

frames = []

RECORD_SECONDS = 5
nchunks = int(RECORD_SECONDS * FRAME_RATE / FRAMES_PERBUFF)
for i in range(0, nchunks):
    data = stream.read(FRAMES_PERBUFF,exception_on_overflow = False)
    frames.append(data) # 2 bytes(16 bits) per channel
print("* done recording")
stream.stop_stream()
stream.close()
p.terminate()


print(map(ord, frames[1][:20]))

import wave
wf = wave.open('recorded_audio.wav', 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(FRAME_RATE)
wf.writeframes(b''.join(frames))
wf.close()
