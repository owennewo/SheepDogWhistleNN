from matplotlib.mlab import window_none,window_hanning,specgram
import matplotlib.pyplot as plt
# based on arbitrary duration example
import queue, threading, sys, time
import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

f = "/tmp/rec_threading.wav"

subtype = 'PCM_16'
dtype = 'int16' 
SAMPLERATE = 8000 # divide by 2 to give highest frequency
MAX_CHUNKS = 16
MAX_FRAMES = int(SAMPLERATE / 2)


q = queue.Queue()
recorder = False

frame_count = 0

frame_buffer = []

def find_usb_device(self):
    devices = sd.query_devices()
    for index, device in enumerate(devices):
        name = device["name"]
        if "USB" in name:
            print("found", index, device["name"])
            return index
    print ("Found no sound devices matching USB")
    exit(1)

device_id = find_usb_device()


def rec():
    with sf.SoundFile(f, mode='w', samplerate=SAMPLERATE, 
                      subtype=subtype, channels=1) as file:
        with sd.InputStream(device = device_id, 
                            samplerate=SAMPLERATE, 
                            dtype=dtype, 
                            channels=1, 
                            callback=save):
            while getattr(recorder, "record", True):
                file.write(q.get())

def save(indata, frames, time, status):
    global frame_count, frame_buffer
    newdata = numpy.reshape(indata, newshape=(indata.shape[0]))
    # numpy.append(frame_buffer,indata)
    print("meta", newdata.shape)
    frame_buffer = numpy.hstack((frame_buffer,newdata))
    sample_count = frame_buffer.shape[0]
        
    if ( sample_count > MAX_FRAMES):
        print("size", frame_buffer.shape, MAX_FRAMES)
        frame_buffer = numpy.delete(frame_buffer,numpy.s_[0:-(MAX_FRAMES)])

    print("shape", indata.shape, frames, frame_buffer.shape)
    frame_count = frame_count + frames
    q.put(indata.copy())

def start():
    global recorder
    recorder = threading.Thread(target=rec)
    recorder.record = True
    recorder.start()

def stop():
    global recorder
    recorder.record = False
    recorder.join()
    recorder = False

# main
print('start recording')
start()
time.sleep(1)
stop()
print("frame_count", frame_count)
print('stop recording')


LOW_FREQ = 500
HIGH_FREQ = 2000
CHANNELS = 1
FRAMES_PERBUFF = 256 #number of samples to take per read
IMAGE_SIZE = 32#height and width of image
SPECGRAM_NFFT = 256 #IMAGE_SIZE * 2 -1  # this effects how many bins of frequency
SPECGRAM_OVERLAP = 0 # max == NFFT - 1
count = 0

arr2D,freqs,bins = specgram(frame_buffer,
                                window=window_hanning,
                                Fs = SAMPLERATE,
                                NFFT=SPECGRAM_NFFT,
                                noverlap=SPECGRAM_OVERLAP,
                                detrend='mean', 
                                mode='psd')

print("specgram", arr2D.shape, freqs[-1], bins[-1])
extent = (bins[0],bins[-1]*MAX_CHUNKS,freqs[-1],freqs[0])
im = plt.imshow(arr2D, 
                    cmap='hot',
                    aspect='auto',
                    extent=extent)
plt.ylim(LOW_FREQ, HIGH_FREQ) #max freqency is half rate

plt.show()
