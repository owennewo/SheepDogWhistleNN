from matplotlib.mlab import window_hanning,specgram
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np  # Make sure NumPy is loaded before it is used in the callback
# assert np  # avoid "imported but unused" message (W0611)

# I can whistle between 500 Hz to 2000 Hz
IMAGE_SIZE = 32
SAMPLERATE = 8000
MAX_FREQ = SAMPLERATE / 2
LOW_FREQ = 500 
HIGH_FREQ = 2000
SPECGRAM_NFFT = int((IMAGE_SIZE*2 - 1) * MAX_FREQ / (HIGH_FREQ - LOW_FREQ))# this effects how many bins of frequency (specgram y-axis)
print(SPECGRAM_NFFT)
# exit(0)
SPECGRAM_OVERLAP = 0 # max == NFFT - 1
 
MAX_CHUNKS = 16
MAX_FRAMES = int(SAMPLERATE)

class ui_common():

    title = "foobar"
    fig = None
    count = 0
    image = None
    image_data = None #2d 
    frame_buffer = []
    data_ready = False
    initialized = False
    stream = None
    closed = False


    def __init__(self, callback):
        print("ui initialized")
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
    
    def close(self):
        print("Closing")
        count = 0
        self.stream.close()
        plt.close()
        self.closed = True

    def new_frames(self, indata, frames, time, status):
        newdata = np.reshape(indata, newshape=(indata.shape[0]))
        self.frame_buffer = np.hstack((self.frame_buffer,newdata))
        sample_count = self.frame_buffer.shape[0]  
        if ( sample_count > MAX_FRAMES):
            self.frame_buffer = np.delete(self.frame_buffer,np.s_[0:-(MAX_FRAMES)])
            self.data_ready = True
            

    def set_title(self, title):
        # print(title)
        self.title.set_text(title)

    def get_specgram(self, data):
        image_data,freqs,bins = specgram(data,
                                    window=window_hanning,
                                    Fs = SAMPLERATE,
                                    NFFT=SPECGRAM_NFFT,
                                    noverlap=SPECGRAM_OVERLAP,
                                    detrend='mean', 
                                    mode='psd')
        return (image_data, freqs, bins)
    
    def updateImage(self):
        if not self.data_ready:
            # print("not ready")
            return False
        self.data_ready = False
        self.image_data,freqs,bins = self.get_specgram(self.frame_buffer)


        low_index = int(self.image_data.shape[0] * LOW_FREQ/MAX_FREQ)
        high_index = int(self.image_data.shape[0] * HIGH_FREQ/MAX_FREQ)
        # slicing out the 32x32 image data.  i.e. 500Hz to 2000Hz and last 32 pixels
        self.image_data = self.image_data[low_index:high_index,-32:]


        self
        
        if self.initialized:
            self.image.set_array(self.image_data)
            self.fig.canvas.start_event_loop(0.001) # or plt.pause(0.05)
        else:     
            print("initializing specgram", self.image_data.shape, freqs[-1], bins[-1])
            extent = (bins[0],bins[-1]*MAX_CHUNKS,HIGH_FREQ, LOW_FREQ) #freqs[-1],freqs[0])
            self.image = self.ax.imshow(self.image_data, 
                                cmap='gray',
                                aspect='auto',
                                extent=extent)
            self.initialized = True
        return True
            
    
    def start(self, device_id, close_on_exit = False):
        plt.ion()
        plt.show(block=False)
        
        self.stream = sd.InputStream(device = device_id, 
                                samplerate=SAMPLERATE, 
                                dtype='int16', 
                                channels=1, 
                                callback=self.new_frames)
        self.stream.start()
        self.fig, self.ax = plt.subplots()
        if close_on_exit:
            self.fig.canvas.mpl_connect('close_event', exit)
        plt.ylim(LOW_FREQ, HIGH_FREQ)
        self.title = self.ax.text(0.5,0.1, "", bbox={'alpha':0.6}, transform=self.ax.transAxes)
        self.closed = False

        while(not self.closed):
            if self.updateImage():
                self.count = self.count +1
                self.callback(self, self.count)

def example_callback(owner,count):
    owner.set_title(f"image{count}")
    # print(owner.image_data.shape)

def main():
    ui = ui_common(example_callback)
    device_id = ui.find_usb_device()
    ui.start(device_id, close_on_exit=True)

if __name__ == "__main__":
    main()
