from ui_common import ui_common
from matplotlib.pyplot import imsave
import sys, os
from torchvision.utils import save_image
import torch
import numpy as np

np.set_printoptions(threshold = sys.maxsize)

image_classification = None # what image classification are we recording
image_index = 0
image_count = 10 # how many images do we want to record

def save_callback(owner, count):
    global image_index, image_classification
    if count%3 == 0:
        image_index = image_index + 2
        filename = f"images/{image_classification}/extra-{count}" 
        ui.set_title(filename)
                
        if (image_index > image_count):
            print(f"we have recorded {image_index - 1} images")
            ui.close()
            # plt.close()
            print("plot closed")  
        else:
            # 3 approaches to saving

            # save 1 using save_image (problem seems to have noise - vertical strips)
            # save_image(torch.from_numpy(np.flip(owner.image_data,0).copy()),filename)
            
            
            # save 2 using savefig (problem - diffiful to set exact size e.g. 32x32)
            # owner.ax.set_axis_off()
            # owner.fig.savefig(filename,bbox_inches='tight', pad_inches=0)
            
            # save#3 using imsave (goldilocks!)
            image_data =np.flip(owner.image_data,0).astype(np.int)
            imsave(f"{filename}.png", image_data, cmap='gray', format='png')
            np.save(f"{filename}.npy",image_data)

            print("saving", image_index, filename, image_data.shape)

def main():
    global image_index, image_classification, image_count, ui

    if (len(sys.argv) < 2):
        print(f"ui_record.py <image_count> {sys.argv}")
        sys.exit(1)

    image_count = int(sys.argv[1])

    while True:
        image_index = 0
        image_classification = input("enter new classification name:")
        image_dir = f"images/{image_classification}"

        if image_classification == "":
            print("exiting")
            sys.exit(0)

        if not os.path.exists(image_dir):
            print(f"creating dir {image_dir}")
            os.makedirs(image_dir) 
        
                
        ui = ui_common(callback=save_callback)
        # ui = ui_common(example_callback)
        device_id = ui.find_usb_device()
        ui.start(device_id)
        print(f"Done {image_classification}")

if __name__ == "__main__":
    main()
