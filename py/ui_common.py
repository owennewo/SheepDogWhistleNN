from matplotlib.mlab import window_none,window_hanning,specgram
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.colors import LogNorm
import pyaudio
import numpy as np

LOW_FREQ = 500
HIGH_FREQ = 2000
RATE = HIGH_FREQ * 2
CHUNK_SIZE = 500 #number of samples to take per read
MAX_CHUNKS = 32
IMAGE_SIZE = 32#height and width of image
NFFT = IMAGE_SIZE * 2 -1  # this effects how many bins of frequency
OVERLAP = 0 # max == NFFT - 1
count = 0


folder_name="images/noop"
# folder_name="images/none"

class ui_common():

    title = "foobar"
    figsize = None

    def __init__(self, callback):
        print("specgram initialized")
        self.callback = callback

    def start(self):

        px = 1/plt.rcParams['figure.dpi']
        self.figsize = (64*px, 64*px)
        # print(f"figure size = {self.figsize}")
        fig, ax = plt.subplots()
        
        ax.axis("off")
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        title = ax.text(0.5,0.1, "", bbox={'facecolor':'w', 'alpha':0.5, 'pad':10},
                transform=ax.transAxes, ha="center")
        
        stream,pa = self.open_mic()
        arr2D,freqs,bins = self.get_specgram(stream)

        print(f"#bin={len(bins)} #freq={len(freqs)}")
        
        extent = (bins[0],bins[-1]*MAX_CHUNKS,freqs[-1],freqs[0])
        image = ax.imshow(arr2D, aspect='auto',interpolation="none",extent = extent,
                        norm = LogNorm(vmin=.01,vmax=1), cmap = 'gray') # cmap = 'jet'

        plt.ylim(LOW_FREQ, HIGH_FREQ) #max freqency is half rate

        anim = animation.FuncAnimation(fig,self.update_fig,blit = True,
                                    interval=1000 * CHUNK_SIZE /  (RATE * 4))

        self.title = title
        self.ax = ax
        self.image = image
        self.stream = stream
                                    
        try:
            plt.show()
            
        except:
            print("Plot Closed")

        stream.stop_stream()
        stream.close()
        pa.terminate()
        print("Program Terminated")

    def set_title(self, title):
        print(title)
        self.title.set_text(title)

    def close(self):
        print("Closing")
        count = 0
        plt.close()

    def open_mic(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format = pyaudio.paInt16,
                        channels = 1,
                        rate = RATE,
                        input = True,
                        frames_per_buffer = CHUNK_SIZE)
        return stream,pa

    def get_specgram(self, stream):
        input_data = stream.read(CHUNK_SIZE)
        data = np.frombuffer(input_data,np.int16)
        arr2D,freqs,bins = specgram(data,window=window_hanning,
                                    Fs = RATE,NFFT=NFFT,noverlap=OVERLAP,detrend='mean', mode='psd')
        return arr2D,freqs,bins

    def update_fig(self,n):
        global count
        count = count + 1

        arr2D,freqs,bins = self.get_specgram(self.stream)
        # print(self.image)
        
        im_data = self.image.get_array()
        im_data = np.hstack((im_data,arr2D))
        
        sample_count = im_data.shape[1]
        
        if ( sample_count > MAX_CHUNKS):
            im_data = np.delete(im_data,np.s_[0:-(MAX_CHUNKS)] ,1)

        self.image.set_array(im_data)
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
    ui.start()
    ui.set_title("ddd")


if __name__ == "__main__":
    main()
