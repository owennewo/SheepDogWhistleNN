import os, sys
import torch
from matplotlib.pyplot import imsave
from nn_common import NumpyDataset


print(torch.__version__)

from ui_common import ui_common
import nn_common as common
import numpy as np
from torchvision.utils import save_image

import serial_port as comms
import time
ports = comms.serial_ports()
if len(ports) ==0:
    print("No serial ports, exiting")
    exit(0)
print(ports)
device = "/dev/ttyUSB0"
if device in ports:
    print(f"found {device}")
    comms.connect(device)
else:
    print(f"not found {device}")
    exit(1)


dataset = NumpyDataset("augmented",fetch=False)
labels = dataset.get_labels()

np.set_printoptions(threshold = sys.maxsize)

last_prediction = ""
same_count = 0

if not torch.cuda.is_available():
    print("torch says you have no cuda.  Aborting")
    exit(1)

os.makedirs('test/dummy', exist_ok=True)

transform = common.get_transform()
net = common.create_net(True)
device = common.get_device()

def predict_callback(owner, count):
    global last_prediction, same_count
    image_data = np.flip(owner.image_data,0).astype(np.int)
        
    if image_data[8:-8,8:-8].max() > 80:
        
        image = torch.from_numpy(image_data.copy()).to(device).float()
        inputs = image.view(1, -1)
        outputs = net(inputs)
        output = outputs.cpu().detach().numpy()[0]

        label_index = np.argmax(output)
        new_prediction = labels[label_index]
        filename = f"images/{count}-{new_prediction}"
    else:
        new_prediction = "silence"
        # return

    if last_prediction == new_prediction:
        same_count = same_count + 1
        
    else:
        same_count = 0
        # uncertain new prediction
        ui.set_title("?")

    last_prediction = new_prediction

    if (new_prediction != "silence" and same_count == 1) or (new_prediction == "silence" and same_count == 2):
        ui.set_title(f"prediction = {new_prediction}")
        print(new_prediction)
        comms.move(new_prediction)
    elif same_count == 0:
        # only interested in when we have two consecutive reading the same
        ui.set_title(f"")

def main():
    global labels, ui
                
    ui = ui_common(callback=predict_callback)
    device_id = ui.find_usb_device()
    ui.start(device_id)
        
if __name__ == "__main__":
    main()
