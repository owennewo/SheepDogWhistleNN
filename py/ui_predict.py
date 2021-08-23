import os
import torch
from matplotlib.pyplot import imsave

# os.environ['LD_LIBRARY_PATH']="/usr/local/cuda/lib64"
# print("setting LD_LIBRARY_PATH")
print(torch.__version__)
a = torch.cuda.FloatTensor(2).zero_()
print(a)

from ui_common import ui_common
import nn_common as common
import numpy as np
from torchvision.utils import save_image


# PATH="/usr/local/cuda/bin:${PATH}"
# ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

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
    # print(count, owner.image_data.shape)

    image = torch.from_numpy(np.flip(owner.image_data,0).copy()).to(device).float()
    # print(image.shape)
    image = image.view(1, -1)
    # print(image.shape)
    outputs = net(image)
    output = outputs.cpu().detach().numpy()[0]
    class_index = np.argmax(output)
    new_prediction = classes[class_index]
    print(new_prediction)

    # if count%1 == 0:
    #     filename = f"test/dummy/test.png"        
    #     # save 1 using save_image (problem seems to have noise - vertical strips)
    #     # save_image(torch.from_numpy(np.flip(owner.image_data,0).copy()),filename)
         
    #     # save 2 using savefig (problem - diffiful to set exact size e.g. 32x32)
    #     # owner.ax.set_axis_off()
    #     # owner.fig.savefig(filename,bbox_inches='tight', pad_inches=0)
        
    #     # save#3 using imsave (goldilocks!)
    #     imsave(filename, arr=np.flip(owner.image_data,0), cmap='gray', format='png')
                

    #     dataset_loader, _ = common.get_dataloader(transform, 'test')
        
    #     images, labels = next(iter(dataset_loader))
    #     # print(images.size())
    #     images, labels = images.to(device), labels.to(device)
    #     print(images.shape)
    #     images = images.view(1, -1) # torch.Size([1, 784])
    #     print(images.shape)
    #     # print(images.size())
    #     outputs = net(images)

    #     label = labels.cpu().detach().numpy()[0]
    #     output = outputs.cpu().detach().numpy()[0]
    #     class_index = np.argmax(output)
    #     new_prediction = classes[class_index]
    #     if last_prediction == new_prediction:
    #         same_count = same_count + 1
            
    #     else:
    #         same_count = 0
    #         # uncertain new prediction
    #         ui.set_title("?")

    #     last_prediction = new_prediction

    #     if same_count == 1:
    #         ui.set_title(f"prediction = {new_prediction}")
    #     elif same_count > 1:
    #         # only interested in when we have two consecutive reading the same
    #         ui.set_title(f"")
    #     print(new_prediction)

def main():
    global classes, ui
    image_dir = 'images'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    _, classes = common.get_dataloader(transform, image_dir)
   

    while True:

                
        ui = ui_common(callback=predict_callback)
        # ui = ui_common(example_callback)
        device_id = ui.find_usb_device()
        ui.start(device_id)

        
if __name__ == "__main__":
    main()
