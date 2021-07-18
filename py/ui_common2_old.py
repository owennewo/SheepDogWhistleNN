from matplotlib.mlab import window_none,window_hanning,specgram
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.colors import LogNorm
# import pyaudio
import sounddevice as sd
import numpy as np

LOW_FREQ = 500
HIGH_FREQ = 2000
CHANNELS = 1
RATE = 8000 #CHEAP USB only support 44.1K. Laptop mic happy with lower e.g. 4000
FRAMES_PERBUFF = 256 #number of samples to take per read
MAX_CHUNKS = 32
IMAGE_SIZE = 32#height and width of image
NFFT = 32 #IMAGE_SIZE * 2 -1  # this effects how many bins of frequency
OVERLAP = 0 # max == NFFT - 1
count = 0
MAX_FRAMES = 128

frame_buffer = []

class ui_common():

    title = "foobar"
    figsize = None
    initialised = False
    image = None

    def __init__(self, callback):
        print("specgram initialized")
        self.callback = callback

    def find_usb_device(self):
        devices = sd.query_devices()
        for index, device in enumerate(devices):
            name = device["name"]
            if "USB" in name:
                print("found", index, device["name"])
                return index
        print ("Found no sound devices matching USB")
        exit(1)


        # print(devices)
        exit(0)
        # p = pyaudio.PyAudio()
        # for i in range(p.get_device_count()):
        #     name = p.get_device_info_by_index(i)["name"]
        #     print(f"{i}: {name}")
        #     if "USB" in name: 
        #         print(f"USB device is {i}", p.get_device_info_by_index(i))
        #         return i

    def start(self, device_id):
        global ax, fig

        px = 1/plt.rcParams['figure.dpi']
        self.figsize = (64*px, 64*px)
        # print(f"figure size = {self.figsize}")
        fig, ax = plt.subplots()

        # # exit(0)
        
        ax.axis("off")
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        title = ax.text(0.5,0.1, "", bbox={'facecolor':'w', 'alpha':0.5, 'pad':10},
                transform=ax.transAxes, ha="center")
        
        stream = self.open_mic(device_id)
        stream.start()
        
        self.title = title
        self.ax = ax
        # self.image = image
        self.stream = stream
                                    
        # try:
        #     # plt.show()
            
        # except:
        #     print("Plot Closed")

        # stream.stop_stream()
        # stream.close()
        # pa.terminate()
        # print("Program Terminated")
        # while(True):
            # print(".")

    def set_title(self, title):
        print(title)
        self.title.set_text(title)

    def close(self):
        print("Closing")
        count = 0
        plt.close()


    def mic_data(self, indata, frames, time, status):
        global frame_count, frame_buffer, ax, fig
        # print("data!", indata.shape)
        
        arr2D,freqs,bins = self.get_specgram(indata)

        if not self.initialised:
            self.initialised = True
            
            print("=====", indata.shape, arr2D.shape)

            print(f"#bin={len(bins)} #freq={len(freqs)}")
            
            extent = (bins[0],bins[-1]*MAX_CHUNKS,freqs[-1],freqs[0])
            self.image = ax.imshow(arr2D, aspect='auto',interpolation="none",extent = extent,
                            norm = LogNorm(vmin=.01,vmax=1), cmap = 'jet') # cmap = 'jet'

            anim = animation.FuncAnimation(fig,self.update_fig,blit = True,
                                    interval=100) #1000 * FRAMES_PERBUFF /  (RATE * 4))
        
            plt.ylim(LOW_FREQ, HIGH_FREQ) #max freqency is half rate
            plt.show()


# exit(0)
        # newdata = np.reshape(indata, newshape=(indata.shape[0]))
        # # np.append(frame_buffer,indata)
        # print("meta", newdata.shape)
        frame_buffer = self.image.get_array()
        frame_buffer = np.hstack((frame_buffer,arr2D))
        sample_count = frame_buffer.shape[1]
            
        if ( sample_count > MAX_FRAMES):
        #     print("size", frame_buffer.shape, MAX_FRAMES)
            frame_buffer = np.delete(frame_buffer,np.s_[0:-(MAX_FRAMES)],1)

        
        # print("XXX",frame_buffer.shape)
        # self.image.set_array(frame_buffer)

        # print("shape", indata.shape, frames, frame_buffer.shape)
        # frame_count = frame_count + frames
        # q.put(indata.copy())

    def open_mic(self, device_id):
        
        stream = sd.InputStream(device = 6, samplerate=RATE, dtype='int16', 
                            channels=1, callback=self.mic_data)

        # stream = pa.open(format = pyaudio.paInt16,
        #                 channels = CHANNELS,
        #                 input_device_index=device_id,
        #                 rate = RATE,
        #                 input = True,
        #                 frames_per_buffer = FRAMES_PERBUFF)
        # print(dir(stream))
        print(stream._dtype)
        return stream

    def get_specgram(self, input_data):
        # input_data = stream.read(FRAMES_PERBUFF)
        input_data = np.frombuffer(input_data,np.int16)
        arr2D,freqs,bins = specgram(input_data,window=window_hanning,
                                    Fs = RATE,NFFT=NFFT,noverlap=OVERLAP,detrend='mean', mode='psd')
        return arr2D,freqs,bins

    def update_fig(self,n):
        global count
        count = count + 1

        print(".")

        arr2D,freqs,bins = self.get_specgram(frame_buffer)
        # print(self.image)
        
        im_data = self.image.get_array()
        im_data = np.hstack((im_data,arr2D))
        
        sample_count = im_data.shape[1]
        
        if ( sample_count > MAX_CHUNKS):
            im_data = np.delete(im_data,np.s_[0:-(MAX_CHUNKS)] ,1)

        self.image.set_array(im_data)
        # plt.draw()
        # print(self.image, im_data.size, im_data.shape, arr2D.shape, len(bins), len(freqs))
        
        if count % 5 == 0:
            if (self.callback):
                self.callback(im_data, count)
        return (self.image, self.title)

def save_callback(data, count):
    ui.set_title(count)
    

def main():
    global ui

    ui = ui_common(callback=save_callback)
    device_id = ui.find_usb_device()


    ui.start(device_id)
    ui.set_title("ddd")


if __name__ == "__main__":
    main()
