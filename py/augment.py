import os
import sys
import torch
from matplotlib.pyplot import imread, imsave
from PIL import Image
import numpy as np

AUGMENT_BORDER = 6 # we'll ignore images that have no bright pixels in the center 

def augment(image_data, shift_x, shift_y):

    # shift columns (shift_x)
    image_data = np.roll(image_data, shift_x, axis=1)
    if shift_x >= 0:
        image_data[:,0:shift_x] = 0
    elif shift_x < 0:
        image_data[:,shift_x:] = 0

    #shift rows (shift_y) and zero
    image_data = np.roll(image_data, shift_y, axis=0)
    if shift_y >= 0:
        image_data[0:shift_y,:] = 0
    elif shift_y < 0:
        image_data[shift_y:,:] = 0

    # print(image_data)
    # print(image_data.shape)

    return image_data

def image_valid(image_data, classname):
    # we want data in central area
    if image_data[AUGMENT_BORDER:-AUGMENT_BORDER,AUGMENT_BORDER:-AUGMENT_BORDER].max() > 40 or classname == "silence":
        return True
    else:
        return False

def augment_image(folder, classname, filename):

    source_filename = f"{folder}/{classname}/{filename}"
    source_prefix = filename.split(".")[0]
    VERTICAL_SHIFT = 3
    HORIZONTAL_SHIFT = 5
    x_range = range(-HORIZONTAL_SHIFT, HORIZONTAL_SHIFT +1)
    y_range = range(-VERTICAL_SHIFT, VERTICAL_SHIFT +1)

    image_data = Image.open(source_filename).convert('L')
    image_data = np.asarray(image_data)

    for x in x_range:
        for y in y_range:

            image_aug = augment(image_data, x, y)
            aug_filename = f"augmented/{classname}/{source_prefix}_{x}{y}.png"
            
            if image_valid(image_aug, classname):
                print (x, y, aug_filename, image_aug[:-5,5:-5].max())
                imsave(aug_filename, arr=image_aug, cmap='gray', format='png')
            else:
                print(f"skipping {aug_filename}")

def augment_npy(folder, classname, filename):

    

    # if(classname!="click"):
    #     return

    source_filename = f"{folder}/{classname}/{filename}"
    source_prefix = filename.split(".")[0]
    VERTICAL_SHIFT = 3
    HORIZONTAL_SHIFT = 5
    x_range = range(-HORIZONTAL_SHIFT, HORIZONTAL_SHIFT +1)
    y_range = range(-VERTICAL_SHIFT, VERTICAL_SHIFT +1)

    image_data = np.load(source_filename)
    # print(image_data)
    for x in x_range:
        for y in y_range:
            
            image_aug = augment(image_data, x, y)
            aug_filename = f"augmented/{classname}/{source_prefix}_{x}{y}"
            
            if image_valid(image_aug, classname):
                # print (f"{aug_filename}.npy")
                np.save(f"{aug_filename}.npy", image_aug)
                # imsave(f"{aug_filename}.png", arr=image_aug, cmap='gray', format='png')
            else:
                print(f"skipping {aug_filename}")

def main():

    source_folder = "images"
    # os.mkdir("augmented", exist_ok=True)
    for class_folder in os.listdir(source_folder):
        print(class_folder)
        os.makedirs(f"augmented/{class_folder}", exist_ok=True)
        for filename in os.listdir(f"{source_folder}/{class_folder}"):
            # print(f" - {class_folder}/{filename}")
            
            # if filename.endswith("png"):
                # augment_image(source_folder, class_folder, filename)

            if filename.endswith("npy"):
                augment_npy(source_folder, class_folder, filename)
     
            
if __name__ == "__main__":
    main()
