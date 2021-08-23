from torch._C import dtype
import nn_common as common

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from nn_common import NumpyDataset

EPOCHS = 20
BATCH_SIZE = 256
TRAIN_SPLIT = 0.9
PRINT_INTERVAL = 10
LEARNING_RATE = 0.003
MOMENTUM = 0.9

transform = common.get_transform()
dataset = NumpyDataset('./augmented')
dataset_size = len(dataset)
train_size = int(TRAIN_SPLIT * dataset_size)
val_size = dataset_size - train_size
print("dataset sizes:", dataset_size, train_size, val_size)

train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])


train_dataloader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
val_dataloader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=True)

# dataset_loader, _ = common.get_npy_dataloader(transform,source_folder='./augmented')
net = common.create_net(False)
device = common.get_device()

loss_function = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=LEARNING_RATE, momentum=MOMENTUM)

# dataset_loader

print("starting")

for epoch in range(EPOCHS):  # loop over the dataset multiple times

    print("######################### epoch", epoch + 1)
    running_loss = 0.0
    print_size = 0
    
    for i, data in enumerate(train_dataloader, 0):

        inputs, labels = data
        # inputs = inputs.to(device).float()
        labels = labels.to(device)
        batch_size = labels.size()[0]
        print_size = print_size + batch_size
        inputs = inputs.contiguous().view(batch_size, -1).to(device).type(torch.cuda.FloatTensor)
        # labels = torch.tensor([label], dtype=torch.long, device=device)
        

        optimizer.zero_grad()
        outputs = net(inputs)
        loss = loss_function(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item() * batch_size

        if i % PRINT_INTERVAL == (PRINT_INTERVAL -1):    # print every 2000 mini-batches
            print(f"epoch:{epoch + 1} batch:{i + 1} ({BATCH_SIZE * (i+1)}) loss: {running_loss / print_size:.3f}")
            running_loss = 0.0
            print_size = 0

    validation_loss = 0
    for i, data in enumerate(val_dataloader, 0):

        inputs, labels = data
        # inputs = inputs.to(device).float()
        labels = labels.to(device)
        batch_size = labels.size()[0]
        inputs = inputs.contiguous().view(batch_size, -1).to(device).type(torch.cuda.FloatTensor)
        # labels = torch.tensor([label], dtype=torch.long, device=device)
        

        # optimizer.zero_grad()
        outputs = net(inputs)
        loss = loss_function(outputs, labels)
        # loss.backward()
        # optimizer.step()

        # print statistics
        validation_loss += loss.item() * batch_size

        if i % PRINT_INTERVAL == (PRINT_INTERVAL -1):    # print every 2000 mini-batches
            print(f"epoch:{epoch + 1} batch:{i + 1} ({BATCH_SIZE * (i+1)}) validation")
            # running_loss = 0.0
    
    print(f"validation loss: {validation_loss/len(val_set)}")
    print("#######################")

print('Finished Training')

PATH = './whistle_net.pth'
torch.save(net.state_dict(), PATH)

print("net saved to ", PATH)
