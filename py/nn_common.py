import torch
from torchvision import transforms, datasets

import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim
from torchvision.transforms.transforms import Grayscale
import numpy as np

IMAGE_WIDTH=32
IMAGE_HEIGHT=32
INPUT_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT
OUTPUT_SIZE = 5 # number of classifications

HIDDEN1_SIZE = 16
HIDDEN2_SIZE = 32

NET_PATH = './whistle_net.pth'

class WhistleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(INPUT_SIZE, HIDDEN1_SIZE)
        self.fc2 = nn.Linear(HIDDEN1_SIZE, HIDDEN2_SIZE)
        self.fc3 = nn.Linear(HIDDEN2_SIZE, OUTPUT_SIZE)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return torch.softmax(x, dim=-1)


def get_device():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)
    return device

def create_net(load = True):

    net = WhistleNet()
    if load:
        net.load_state_dict(torch.load(NET_PATH))
    net.to(get_device())
    return net

def get_transform():

    data_transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.ToTensor()
        ])
    return data_transform

def get_dataloader(data_transform, source_folder='./images'):
    whistle_dataset = datasets.ImageFolder(root=source_folder,
                                       transform=data_transform)
    classification_map = whistle_dataset.classes
    dataset_loader = torch.utils.data.DataLoader(whistle_dataset,
                                             batch_size=1, shuffle=True,
                                             num_workers=4)
    return dataset_loader, classification_map
