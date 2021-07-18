from ui_common import ui_common
import sys, os
from torchvision.utils import save_image
import torch
import numpy as np


image_classification = None # what image classification are we recording
image_index = 0
image_count = 10 # how many images do we want to record

def save_callback(owner, count):
    global image_index, image_classification
    image_index = image_index + 1
    filename = f"images/{image_classification}/{count}.png"        
    ui.set_title(filename)
            
    if (image_index > image_count):
        print(f"we have recorded {image_index - 1} images")
        ui.close()
        # plt.close()
        print("plot closed")  
    else:
        # copy = data
        # print(np.sum(copy))
        # if np.sum(copy) == 0:
        #     print("EMPTY ***********************")
        # cv2.imwrite(filename, data)
        # save_image(torch.from_numpy(owner.image_data),filename)
        # save_image(torch.from_numpy(data)/255, filename, nrow=1, normalize=True)
        print("saving", image_index, filename, owner.image_data.shape)
        # plt.savefig(filename, figsize=figsize)

def main():
    global image_index, image_classification, image_count, ui

    if (len(sys.argv) != 2):
        print('ui_record.py <image_count>')
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
        ui.start()
        print("?")
        print(f"Done {image_classification}")

if __name__ == "__main__":
    main()
