from mpl_toolkits.axes_grid1 import ImageGrid
import matplotlib.pyplot as plt
import numpy as np


def vis_brain(image, slice_sel, 
            axis_sel=1, 
            normalize=False, 
            figsize=(7.0,7.0),
            vmin=None, vmax=None,
            cmap='gray'):
    """Plot single slice.
    
    Args:
        image (3darray): image data
        slice_sel (int): selected slice number
        axis_sel (int, optional): Select axis (0,1,2) Defaults to 1.
        normalize (bool, optional): Apply z-normalization. Defaults to False.
        figsize (tuple, optional): Size of the figure. Defaults to (7.0,7.0)).
        vmin (float, optional): Min. intensity value. Defaults to None.
        vmax (float, optional): Max. intensity value. Defaults to None.
        cmap (string, optional): Colormap. Defaults to 'gray'.
    """
    if normalize:
        image = (image - np.mean(image))/(np.std(image))

    if axis_sel == 1:
        image = image.transpose([1, 2, 0])
    elif axis_sel == 2:
        image = image.transpose([2, 0, 1])

    fig = plt.figure(figsize=figsize)
    im = image[slice_sel, :, :]

    if not vmin or not vmax:
        plt.imshow(im, cmap='gray')
    else:
        plt.imshow(im, cmap='gray', vmin=vmin, vmax=vmax)
    plt.axis('off')
    plt.show()


def vis_brain_grid(image, axis_sel=1, n_slices=9, 
                   normalize=True,
                   figsize=(15., 15.),
                   vmin=None, vmax=None, cmap='gray'):
    """Plots a grid
    
    Args:
        image (3darray): image data
        axis_sel (int, optional): Select axis (0,1,2) Defaults to 1.
        n_slices (int, optional): Number of slices should be a multiple of three. Defaults to 9.
        normalize (bool, optional): Apply z-normalization. Defaults to True.
        figsize (tuple, optional): Size of the figure. Defaults to (7.0,7.0)).
        vmin (float, optional): Min. intensity value. Defaults to None.
        vmax (float, optional): Max. intensity value. Defaults to None.
        cmap (string, optional): Colormap. Defaults to 'gray'.
    """
    # n_slices should me a multiple of three.
    max_slices = image.shape[axis_sel+1]
    if normalize:
        image = (image - np.mean(image))/(np.std(image))

    image = image[0, ...]
    if axis_sel == 1:
        image = image.transpose([1, 2, 0])
    elif axis_sel == 2:
        image = image.transpose([2, 0, 1])

    image_list = [image[max_slices//n_slices*k, :, :] for k in range(n_slices)]

    fig = plt.figure(figsize=figsize)
    grid = ImageGrid(fig, 111,  # similar to subplot(111)
                     nrows_ncols=(3, 3),  # creates 2x2 grid of axes
                     axes_pad=0.1,  # pad between axes in inch.
                     )

    for ax, im in zip(grid, image_list):
        if not vmin or not vmax:
            ax.imshow(im, cmap=cmap)
        else:
            ax.imshow(im, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.axis('off')
    plt.show()
