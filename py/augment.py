import os
import sys
import torch
from matplotlib.pyplot import imread, imsave
from PIL import Image
import numpy as np



def augment(filename, shift_x, shift_y):

    image = Image.open(filename).convert('L')
    image = np.asarray(image)

    # shift columns (shift_x)
    image = np.roll(image, shift_x, axis=1)
    if shift_x >= 0:
        image[:,0:shift_x] = 0
    elif shift_x < 0:
        image[:,shift_x:] = 0

    #shift rows (shift_y) and zero
    image = np.roll(image, shift_y, axis=0)
    if shift_y >= 0:
        image[0:shift_y,:] = 0
    elif shift_y < 0:
        image[shift_y:,:] = 0

    # print(image)
    # print(image.shape)

    return image

def image_valid(image_data, classname):
    # we want data in central area
    if image_data[5:-5,5:-5].max() > 80 or classname == "silence":
        return True
    else:
        return False

def augment_image(folder, classname, filename):

    source_filename = f"{folder}/{classname}/{filename}"
    source_prefix = filename.split(".")[0]
    x_range = range(-5, 6)
    y_range = range(-3, 4)
    for x in x_range:
        for y in y_range:

            image_aug = augment(source_filename, x, y)
            aug_filename = f"augmented/{classname}/{source_prefix}_{x}{y}.png"
            
            if image_valid(image_aug, classname):
                print (x, y, aug_filename, image_aug[:-5,5:-5].max())
                imsave(aug_filename, arr=image_aug, cmap='gray', format='png')
            else:
                print(f"skipping {aug_filename}")

def main():

    source_folder = "images"
    # os.mkdir("augmented", exist_ok=True)
    for class_folder in os.listdir(source_folder):
        print(class_folder)
        os.makedirs(f"augmented/{class_folder}", exist_ok=True)
        for filename in os.listdir(f"{source_folder}/{class_folder}"):
            print(f" - {class_folder}/{filename}")
            augment_image(source_folder, class_folder, filename)

        # filename = f"test/dummy/test.png"  
        # augment_image(filename)            
            
if __name__ == "__main__":
    main()
