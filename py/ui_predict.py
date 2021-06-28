from ui_common import ui_common
import nn_common as common
import os
import numpy as np
from torchvision.utils import save_image
import torch


os.makedirs('test/dummy', exist_ok=True)

transform = common.get_transform()
net = common.create_net(True)
device = common.get_device()

def predict_callback(data, count):
    filename = f"test/dummy/test.png"        
    save_image(torch.from_numpy(data),filename)

    dataset_loader, _ = common.get_dataloader(transform, 'test')
    
    images, labels = next(iter(dataset_loader))
    # print(images.size())
    images, labels = images.to(device), labels.to(device)

    images = images.view(1, -1) # torch.Size([1, 784])
    # print(images.size())
    outputs = net(images)

    label = labels.cpu().detach().numpy()[0]
    output = outputs.cpu().detach().numpy()[0]
    class_index = np.argmax(output)
    ui.set_title(f"prediction = {classes[class_index]}")

def main():
    global classes, ui
    _, classes = common.get_dataloader(transform, 'images')
   

    while True:
        ui = ui_common(callback=predict_callback)
        ui.start()

if __name__ == "__main__":
    main()
