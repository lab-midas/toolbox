import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.widgets import Slider, Button


class MRISlider:
    """
    Visualization of mri images in the nii format, including a Slider and a Label Toggle Button
    """

    def __init__(self, 
                data, 
                label, 
                slice_axis=2,
                vmin=0.0, vmax=10.0, 
                cmap='coolwarm', 
                alpha=0.0,
                custom_plot=None):                
        """ Sets up the Figure

        Args:
            data (float array): image data
            label (float array): label data
            vmin (float, optional): min. intensity value. Defaults to 0.0.
            vmax (float, optional): max. intensity value. Defaults to 10.0.
            cmap (str, optional): colormap. Defaults to 'coolwarm'.
            alpha (float, optional): overlay alpha. Defaults to 0.0.
            custom_plot (function, optional): Customized plot function (replaces default_plot). Defaults to None.
        """
        # todo select slice axis
        self.data = data
        self.label = label
        self.masked_labels = np.ma.masked_where(self.label == 0, self.label)

        self.fig, axis = plt.subplots()

        self.slider, self.button_toggle, self.button_untoggle = self.create_widgets()

        self.slider.on_changed(self.update)
        self.button_toggle.on_clicked(self.toggle_label)
        self.button_untoggle.on_clicked(self.untoggle_label)

        if custom_plot:
            self.mri_slice, self.label_slice = custom_plot(
                    axis, self.data, self.masked_labels)
        else:
            self.mri_slice, self.label_slice = self.default_plot(
                axis, self.data, self.masked_labels, 
                vmin=vmin, vmax=vmax, cmap=cmap, alpha=alpha)

    @staticmethod
    def default_plot(axis, data, masked_labels,
                     vmin=0.0, vmax=10.0,
                     cmap='coolwarm',
                     alpha=0.0):
        """Plot mri data to axis with label overlay.
        
        Args:
            axis (obj): plot axis
            data (array): image data
            masked_labels (masked array): label data
            vmin (float, optional): min. intensity value. Defaults to 0.0.
            vmax (float, optional): max. intensity value. Defaults to 10.0.
            cmap (str, optional): colormap. Defaults to 'coolwarm'.
            alpha (float, optional): overlay alpha. Defaults to 0.0.
        
        Returns:
            (obj, obj): Data and label plot.
        """
        plt_data = axis.imshow(data[:, :, 0], cmap="gray", vmin=vmin, vmax=vmax)
        plt_label = axis.imshow(masked_labels[:, :, 0], alpha=alpha, cmap=cmap)
        return plt_data, plt_label

    def create_widgets(self):
        """
        Creates the widgets: Slider and two Buttons for showing the Labels and removing them
        Args:
            None
        """

        ax_slider = plt.axes([0.25, 0.03, 0.5, 0.03])
        ax_label = plt.axes([0.8, 0.05, 0.1, 0.03])
        ax_no_label = plt.axes([0.8, 0.02, 0.1, 0.03])

        slider = Slider(ax_slider, 'Slice', 0,
                        self.data.shape[-1], valinit=0, valfmt="%i")

        button_toggle = Button(ax_label, "Label")
        button_untoggle = Button(ax_no_label, "No Label")

        return slider, button_toggle, button_untoggle

    def update(self, val):
        """
        Updates the figure when moving the Slider. Connected in init
        Args:
            val (float): Value of the Slider
        """

        slice_index = int(self.slider.val)
        self.mri_slice.set_data(self.data[:, :, slice_index])
        self.label_slice.set_data(self.masked_labels[:, :, slice_index])

        self.fig.canvas.draw_idle()

    def toggle_label(self, event):
        """
        Shows the labels by setting the alpha value to 0.5
        Args:
            event (event): EventTrigger
        """

        self.label_slice.set_alpha(0.5)

    def untoggle_label(self, event):
        """
        Removes the labels by setting the alpha value to 0
        Args:
            event (event): EventTrigger
        """

        self.label_slice.set_alpha(0)


class MRITracker:
    """
    Visualization of mri images in the nii format using mouse scrolling.
    """
    # todo combine with brain plots
    def __init__(self, ax, X):
        self.ax = ax
        ax.set_title('use scroll wheel to navigate images')

        self.X = X
        rows, cols, self.slices = X.shape
        self.ind = self.slices//2

        self.im = ax.imshow(self.X[:, :, self.ind], cmap='gray')
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.ind])
        self.ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()
