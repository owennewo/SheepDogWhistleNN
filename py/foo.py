from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np


def generate_panel(img):
    plt.figure()
    ax = plt.gca()
    fig = plt.gcf()
    implot = ax.imshow(img)
    # When a colour is clicked on the image an event occurs
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show(block=True)


def onclick(event):
    if event.xdata is not None and event.ydata is not None:
        circle = plt.Circle((event.xdata,
                             event.ydata), 2, color='r')
        fig = plt.gcf()
        fig.gca().add_artist(circle)
        plt.draw()
        # Change the contents of the plt window here


if __name__ == "__main__":
    plt.ion()
    img = np.ones((600, 800, 3))
    generate_panel(img)