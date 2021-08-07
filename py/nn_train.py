import nn_common as common

import torch
import torch.nn as nn
import torch.optim as optim

EPOCHS = 5

transform = common.get_transform()
dataset_loader, _ = common.get_dataloader(transform,source_folder='./augmented')
net = common.create_net(False)
device = common.get_device()

loss_function = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.003, momentum=0.9)

# dataset_loader


print("starting")

for epoch in range(EPOCHS):  # loop over the dataset multiple times

    print("######################### epoch", epoch + 1)
    PRINT_INTERVAL = 100
    running_loss = 0.0
    for i, data in enumerate(dataset_loader, 0):
        inputs, labels = data
        inputs, labels = inputs.to(device), labels.to(device)
        inputs = inputs.view(1, -1) # torch.Size([1, 784])

        optimizer.zero_grad()
        outputs = net(inputs)
        loss = loss_function(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()



        if i % PRINT_INTERVAL == (PRINT_INTERVAL -1):    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / PRINT_INTERVAL))
            running_loss = 0.0

print('Finished Training')

PATH = './whistle_net.pth'
torch.save(net.state_dict(), PATH)

print("net saved to ", PATH)
