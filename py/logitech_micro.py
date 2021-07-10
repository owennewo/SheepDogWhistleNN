from matplotlib.mlab import window_hanning,specgram
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np  # Make sure NumPy is loaded before it is used in the callback
assert np  # avoid "imported but unused" message (W0611)

# I can whistle between 500 Hz to 2000 Hz
LOW_FREQ = 500 
HIGH_FREQ = 2000
SPECGRAM_NFFT = 256 #IMAGE_SIZE * 2 -1  # this effects how many bins of frequency
SPECGRAM_OVERLAP = 0 # max == NFFT - 1
SAMPLERATE = 8000 # divide by 2 to give highest frequency
MAX_CHUNKS = 16
MAX_FRAMES = int(SAMPLERATE / 2)

class ui_common():

    title = "foobar"
    fig = None
    count = 0
    image = None
    frame_buffer = []
    data_ready = False
    ready = False

    def __init__(self, callback):
        print("specgram initialized")
        self.callback = callback
            
        # self.fig = plt.figure()
        # self.fig, self.ax = plt.subplots()
 
    def find_usb_device(self):
        devices = sd.query_devices()
        for index, device in enumerate(devices):
            name = device["name"]
            print(index, device["name"])
            if "USB" in name:
                print("found", index, device["name"])
                return index
        print ("Found no sound devices matching USB")
        exit(1)

    def new_frames(self, indata, frames, time, status):
        newdata = np.reshape(indata, newshape=(indata.shape[0]))
        self.frame_buffer = np.hstack((self.frame_buffer,newdata))
        sample_count = self.frame_buffer.shape[0]  
        if ( sample_count > MAX_FRAMES):
            self.frame_buffer = np.delete(self.frame_buffer,np.s_[0:-(MAX_FRAMES)])
            

    def set_title(self, title):
        print(title)
        self.title.set_text(title)

    def get_specgram(self, data):
        arr2D,freqs,bins = specgram(data,
                                    window=window_hanning,
                                    Fs = SAMPLERATE,
                                    NFFT=SPECGRAM_NFFT,
                                    noverlap=SPECGRAM_OVERLAP,
                                    detrend='mean', 
                                    mode='psd')
        return (arr2D, freqs, bins)
    
    def updateImage(self):
        if not self.data_ready:
            print(".")
            # return
        self.data_ready = False
        arr2D,freqs,bins = self.get_specgram(self.frame_buffer)
        
        if self.ready:
            self.image.set_array(arr2D)
            self.fig.canvas.start_event_loop(0.05) # or plt.pause(0.05)
            print("+")
        else:     
            print("specgram", arr2D.shape, freqs[-1], bins[-1])
            extent = (bins[0],bins[-1]*MAX_CHUNKS,freqs[-1],freqs[0])
            self.image = self.ax.imshow(arr2D, 
                                cmap='gray',
                                aspect='auto',
                                extent=extent)
            self.ready = True
            
    
    def start(self, device_id):
        plt.ion()
        plt.show(block=False)
        
        stream = sd.InputStream(device = device_id, 
                                samplerate=SAMPLERATE, 
                                dtype='int16', 
                                channels=1, 
                                callback=self.new_frames)
        stream.start()
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('close_event', exit)
        plt.ylim(LOW_FREQ, HIGH_FREQ)
        self.title = self.ax.text(0.5,0.1, "", bbox={'alpha':0.6}, transform=self.ax.transAxes)

        while(True):
            self.count = self.count +1
            self.updateImage()
            self.callback(self, self.count)

def example_callback(owner,count):
    owner.set_title(f"image{count}")

def main():
    ui = ui_common(example_callback)
    device_id = ui.find_usb_device()
    ui.start(device_id)

if __name__ == "__main__":
    main()
