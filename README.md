# Sheepdog Whistle NN
## Youtube Video

[![Sheepdog Whistle NN](gh_images/thumbnail.png)](https://www.youtube.com/watch?v=YnogVYTpyWo)

## Overview
AI Autonomous vehicles are great but sometimes humans want to influence the robot in the same way that shepherds influence their sheepdogs!  This project explores a whistle control mechanism for a (custom build) jetbot using a [Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit) as the brains and a [Storm32](http://www.olliw.eu/storm32bgc-wiki/Getting_Started) motor controller as the control board.

A pytorch neural net is trained with the following image labels.  

| Example instance | Label | Command |
| ----- | ----- | -----| 
| ![flat](gh_images//flat.png?raw=true "Flat") | Flat | Forward | 
| ![Up](gh_images//up.png?raw=true "Up") | Up | Left |
| ![Down](gh_images//down.png?raw=true "Down") | Down | Right |  
| ![Click](gh_images//click.png?raw=true "Click") | Click | Back! |  
| ![Silence](gh_images//silence.png?raw=true "Silence") | Silence | Stop | 

Live Predictions against this model are then interpretted as a sequence of command which are sent to a 3 wheel self-built 'jetbot'.  A flat whistle sends the bot forward, a rising whistle turns it to the left, a tongue click will send it backwards.

This project has been submitted to the [Jetson AI Specialist Certification](https://developer.nvidia.com/embedded/learn/jetson-ai-certification-programs)

## Audio capture
Code: [py/ui_common.py](py/ui_common.py)

Microphones typically record at sampling rates up to 44.1KHz.  I'm recording at 8K which allows frequencies up to 4K to be detected.    

| Representation | Image | Description |
| ----- | ----- |----- |
| Time domain| ![Time domain](gh_images/time-domain.png) | The standard representation with amplitude (y-axis) against time (x-axis).  It is impossible to to determine that The image on the left contains  flat, up, down, click and silent samples. Unsuitable! |
| Frequency domain | ![Frequency domain](gh_images/frequency-domain.png) | An alternative representation is frequency domain with amplitude (Y axis) against frequency (x-axis).  This is a point-in-time representation making changing pitch difficult to determine. Unsuitable! |
| Spectrogram | ![Spectrogram](gh_images/spectrogram.png) | The chosen representation taken in this project is to use a spectrogram which is a type of heatmap i.e. it can show 3 variables.  Here we have frequency (y-axis) against time (x-axis) with amplitude denoted by color.  Humans and NNs can readily detect whistles represented this way, the diagram to the left is a rising pitch which has been mapped to a 'turn left' command.  Suitable!  |

With the basics out of the way - I've used a few tricks to make things simpler for the NN.  
1) The heatmap is set to grayscale.  The image is therefore 2 dimensional instead of 3 (no separate RGB channels).
2) The frequencies are cropped to only to between 500Hz and 2KHz as this is the frequency I can whistle at.  This also filters out low frequency background noise
3) I've 'binned' the frequencies into 32 bands.  I've also adjusted frame buffer to 32.  This results in an image of 32x32 pixels.  Smaller images train faster.

ui_common.py (which does the above) also displays these images at ~10fps using matplot lib and is the base class to ui_record.py and ui_predicy.py (see below)

## Audio Recording / Collecting labelled samples
code: [py/ui_record.py](py/ui_record.py)

This python is used to capture and label whistle images.  Example usage
 1. ui_record.py 100 (start capture - capturing 100 images per label category)
 2. Loop - enter name of label (e.g. label='flat_pitch')
  a. capture 100 images with user whistling in accordance with the label
  b. save images in label folder (e.g. images/flat_pitch/1.npy)
 3. Repeat loop or end

Originally the images where saved as png files but I switched to npy files as the process of loading/saving numpy arrays to png was slower during prediction

At the end of this process I had recorded about 1000 images in 5 classes (flat, up, down, silence and click).  Some of these samples were poor (bad whistling or whistle was partially out of frame), so the final total was ~500 images

## Sample augmentation
code: [py/augment.py](py/augment.py)

500 images is a low number for NN training, so I turned 500 images into 20,000!  This was done by moving the whisle a few pixels left/right and/or up/down to create shifted new images.  
![augment](gh_images//augment.png?raw=true "augment")

This helps 'fill in the gaps' so that the NN generalises to unseen (unheard?) samples.

My raw and augmented images can be found here, if you want to skip sample capture/labeling/augmentation:
https://drive.google.com/drive/folders/1xyElx27kldVmL93BxWLLImEiT4XyFRHB?usp=sharing

## Training
code: [py/nn_train.py](py/nn_train.py) and [py/nn_common.py](py/nn_common.py)

The setup of the NN is done in nn_common.py (which is used by training and prediction)
We have:
 - cuda enabled pytorch NN.  
 - input layer (1024 nodes) - this receives the 32x32 grayscale pixels
 - 2 hidden layers (16, 32 nodes)
 - output layer (5 nodes) - to match the 5 labels

nn_train.py uses nn_common.py and does the following:
 - I've created a NumpyDataset class to help load the npy files (including classification)
 - loss function is cross entropy
 - optimizer is SGD with vanilla momentum and learning rate (0.9 and 0.003).  These worked well
 - data was split into test/validation.  at the end of each epoch the validation set was used to assess whether NN loss had been minimized.  empirically 20 epochs seemed to be sensible time to stop
 - batch size of 256 seemed to work well on jetson/cuda (a lot fastest than my initial batch size=1!!)
 - the NN was saved as ./whistle_net.pth

 ## Prediction
 code: [py/ui_predict.py](py/ui_predict.py)

 The prediction is a combination of using ui_common.py to collect 10fps images and then passing each numpy array to the NN (whistl_net.pth) for prediction.   The output of the NN is 5 values - representing how much of a match the sample was against each of the 5 labels.  argmax is used to pick out the label with the highest score and thus the prediction is made.

 Once a prediction is made it is 'debounced' a little i.e. we need at least two same predictions in a row to confirm a prediction. The prediction is then sent using py/serial_port.py to the micro controller to the storm32 stm32/arduino board which is the BLDC motor controller.

 ## Storm32 control
 code: [arduino/src/main.cpp](arduino/src/main.cpp)

 The storm32 controller is an affordable (£25) 3 axis bldc motor control board with a powerful stm32f103 mcu on board.  It is usually used in 3-axis gimbal setups but here I'm using it to drive two turnigy ax-2804 100T motors which have great slow speed torque.  The motors are controlled open-loop, the robot would move far smoother if I added some magnetic sensor (e.g. as5600) to close the velocity loop but this would have added cost/complexity.  
 The code uses the SimpleFOC library to manage the complex 3phase FOC control.  I have a lot of experience with this library on other projects and recommend it!

# Hardware
## 3D printed parts

The chassis for this project was 3D printed on an ender 3 pro and designed (by me) using onshape.  

![3d chassis](gh_images/3d-chassis.png?raw=true "3d chassis")

## Other components
 | Part | Description |
 | ----- | ----- |
 | jetson nano 4GB | mounted above chassis plate
 | motor controller | storm32 mounted below chassis plate | 
 | motors | 2x turnigy ax-2804 100T BLDC motors | 
 | Battery | turnigy 1C Transmitter pack (11.1V 2650mAH) | 
 | Buck converter | (Input DC 9-24V, output 5.2V/6A) | 
 | Micophone | Old Logitech USB Microphone for WII singalong game (tried the button microphones but could only sample at 44.1Khz) |
 | Wireless module| Waveshare AC8265 Wireless NIC Applicable for Jetson Nano 2.4G | 
