import torch
import os
from torchvision import transforms, datasets

import torch.utils.data as data

import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim
from torchvision.transforms.transforms import Grayscale
import numpy as np

from typing import Dict, List,  Tuple

IMAGE_WIDTH=32
IMAGE_HEIGHT=32
INPUT_SIZE = IMAGE_WIDTH * IMAGE_HEIGHT
OUTPUT_SIZE = 5 # number of classifications

HIDDEN1_SIZE = 16
HIDDEN2_SIZE = 32

NET_PATH = './whistle_net.pth'

if not torch.cuda.is_available():
    print("torch says you have no cuda.  Aborting")
    exit(1)

class NumpyDataset(data.Dataset):
    """Face Landmarks dataset."""

    def __init__(self, root_dir, transform=None, fetch=True):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_dir = root_dir
        self.transform = transform
        self.items = []
        
        print("reading folders")
        directories = os.listdir(root_dir)
        self.labels = directories
        print("labels are: ", self.labels)
        if(fetch):
            self.fetch_files()
        
    def fetch_files(self):
        self.items = []
        for label in self.labels:
            files = os.listdir(os.path.join(self.root_dir, label))
            print("reading ", label, "files: ", len(files))
            for file in files:
                self.items.append({"label": self.labels.index(label), "label_description": label, "file": os.path.join(self.root_dir, label, file) })


        return self.labels

    def get_labels(self):
        return self.labels

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        
        item = self.items[idx]
        item["data"] = torch.from_numpy(np.load(item["file"]))
        return (item["data"], item["label"])
        # return item

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
    print("device is", device)
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

def get_png_dataloader(data_transform, source_folder='./images'):
    whistle_dataset = datasets.ImageFolder(root=source_folder,
                                       transform=data_transform)
    classification_map = whistle_dataset.classes
    dataset_loader = torch.utils.data.DataLoader(whistle_dataset,
                                             batch_size=1, shuffle=True,
                                             num_workers=4)
    return dataset_loader, classification_map


def get_npy_dataloader(data_transform, source_folder='./images'):
    whistle_dataset = datasets.ImageFolder(root=source_folder,
                                       transform=data_transform)
    classification_map = whistle_dataset.classes
    dataset_loader = torch.utils.data.DataLoader(whistle_dataset,
                                             batch_size=1, shuffle=True,
                                             num_workers=4)
    return dataset_loader, classification_map